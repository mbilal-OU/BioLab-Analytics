"""
bio-lab-calc — Phase 1 (Liquids): CLI + Excel export

Commands:
  1) dilute           -> C1V1 = C2V2
  2) stock-to-working -> e.g., 10X to 1X
  3) serial           -> serial dilution table
  4) molarity         -> grams needed from powder (MW-based)
  5) percent          -> percent solutions (w/v and v/v)

Examples:
  python labcalc.py dilute --c1 "10 mM" --c2 "1 mM" --v2 "50 mL" --export dilution.xlsx
  python labcalc.py stock-to-working --stock "10X" --final "1X" --v2 "500 mL" --export stock.xlsx
  python labcalc.py serial --ratio 10 --steps 6 --vfinal "1 mL" --export serial.xlsx
  python labcalc.py molarity --mw 121.14 --molarity "1 M" --volume "100 mL" --export molarity.xlsx

  # Percent w/v: grams solute for final volume
  python labcalc.py percent --kind wv --percent 10 --final-volume "100 mL" --export sds_10wv.xlsx

  # Percent v/v: mL solute for final volume
  python labcalc.py percent --kind vv --percent 70 --final-volume "500 mL" --export ethanol_70vv_500mL.xlsx
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Literal

import pandas as pd
import pint
import typer
from pydantic import BaseModel, Field, field_validator

app = typer.Typer(add_completion=False)

# -------------------------
# Units setup (Pint)
# -------------------------
ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

# Common aliases students type
ureg.define("uL = microliter = uL")
ureg.define("mL = milliliter = mL")
ureg.define("nM = nanomolar = nM")
ureg.define("uM = micromolar = uM")
ureg.define("mM = millimolar = mM")

MIN_PIPETTABLE = 1 * ureg.uL  # warning threshold (adjust as needed)


# -------------------------
# Helpers
# -------------------------
def q(s: str) -> pint.Quantity:
    """Parse a quantity string like '50 mL' or '10 mM'."""
    try:
        return ureg.Quantity(s)
    except Exception as e:
        raise typer.BadParameter(
            f"Could not parse '{s}'. Use formats like '50 mL', '10 mM', '1 uL'."
        ) from e


def parse_x_factor(s: str) -> float:
    """
    Parse '10X' / '1X' into numeric factor (10, 1).
    Accepts: '10X', '10x', '10 X', '1X'
    """
    cleaned = s.strip().lower().replace(" ", "")
    if not cleaned.endswith("x"):
        raise typer.BadParameter("X factors must end with 'X' (example: 10X, 1X).")
    number = cleaned[:-1]
    try:
        val = float(number)
    except ValueError as e:
        raise typer.BadParameter(
            "Could not parse X factor. Example valid inputs: 10X, 1X, 2.5X."
        ) from e
    if val <= 0:
        raise typer.BadParameter("X factor must be > 0.")
    return val


def format_volume(vol: pint.Quantity) -> str:
    """Format volume nicely, choosing uL/mL/L depending on size."""
    vol = vol.to(ureg.mL)
    if vol.magnitude < 0.001:
        return f"{vol.to(ureg.uL).magnitude:.3g} uL"
    if vol.magnitude < 1:
        return f"{vol.magnitude:.6g} mL"
    if vol.magnitude < 1000:
        return f"{vol.magnitude:.6g} mL"
    return f"{vol.to(ureg.L).magnitude:.6g} L"


def ensure_positive(quantity: pint.Quantity, name: str) -> None:
    if quantity.magnitude <= 0:
        raise typer.BadParameter(f"{name} must be > 0.")


def warn_small_volume(vol: pint.Quantity, label: str) -> Optional[str]:
    if vol.to(ureg.uL) < MIN_PIPETTABLE:
        return (
            f"Warning: {label} = {format_volume(vol)} is < {format_volume(MIN_PIPETTABLE)}. "
            "Consider making an intermediate dilution for accuracy."
        )
    return None


# -------------------------
# Pydantic models for validation
# -------------------------
class DilutionInput(BaseModel):
    c1: str = Field(..., description="Stock concentration e.g. '10 mM'")
    c2: str = Field(..., description="Target concentration e.g. '1 mM'")
    v2: str = Field(..., description="Final volume e.g. '50 mL'")

    @field_validator("c1", "c2", "v2")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty.")
        return v


class StockInput(BaseModel):
    stock: str = Field(..., description="Stock factor e.g. '10X'")
    final: str = Field(..., description="Final factor e.g. '1X'")
    v2: str = Field(..., description="Final volume e.g. '500 mL'")


class SerialInput(BaseModel):
    ratio: float = Field(..., gt=1, description="Dilution ratio per step (e.g., 10 for 1:10)")
    steps: int = Field(..., ge=1, le=100, description="Number of dilution steps (tubes)")
    vfinal: str = Field(..., description="Final volume per tube e.g. '1 mL'")


class MolarityInput(BaseModel):
    mw: float = Field(..., gt=0, description="Molecular weight in g/mol (e.g., 121.14)")
    molarity: str = Field(..., description="Target molarity e.g. '1 M', '50 mM'")
    volume: str = Field(..., description="Final volume e.g. '100 mL', '1 L'")


class PercentInput(BaseModel):
    kind: Literal["wv", "vv"] = Field(..., description="wv for weight/volume, vv for volume/volume")
    percent: float = Field(..., gt=0, le=100, description="Percent value (0-100)")
    final_volume: str = Field(..., description="Final volume e.g. '100 mL', '500 mL'")

    @field_validator("final_volume")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty.")
        return v


# -------------------------
# Core calculations (pure logic)
# -------------------------
@dataclass(frozen=True)
class DilutionResult:
    v1: pint.Quantity
    v_diluent: pint.Quantity
    note: Optional[str]


def calc_dilution(c1: pint.Quantity, c2: pint.Quantity, v2: pint.Quantity) -> DilutionResult:
    """C1V1 = C2V2 -> V1 = (C2*V2)/C1"""
    ensure_positive(c1, "C1")
    ensure_positive(c2, "C2")
    ensure_positive(v2, "V2")

    try:
        c2.to(c1.units)
    except Exception as e:
        raise typer.BadParameter(
            "C1 and C2 must be concentration units (e.g., mM, uM, nM, M) and compatible."
        ) from e

    if c2 >= c1:
        raise typer.BadParameter("Target concentration (C2) must be lower than stock concentration (C1).")

    v1 = (c2 * v2 / c1).to(v2.units)
    if v1 >= v2:
        raise typer.BadParameter("Computed stock volume is >= final volume. Check inputs.")

    v_dil = (v2 - v1).to(v2.units)
    note = warn_small_volume(v1, "Stock volume V1")
    return DilutionResult(v1=v1, v_diluent=v_dil, note=note)


@dataclass(frozen=True)
class StockResult:
    v_stock: pint.Quantity
    v_diluent: pint.Quantity
    note: Optional[str]


def calc_stock_to_working(stock_x: float, final_x: float, v2: pint.Quantity) -> StockResult:
    """Vstock = Vfinal * (final_x/stock_x)"""
    ensure_positive(v2, "V2")
    if final_x >= stock_x:
        raise typer.BadParameter("Final X must be lower than Stock X (e.g., 1X from 10X).")

    v_stock = (v2 * (final_x / stock_x)).to(v2.units)
    v_dil = (v2 - v_stock).to(v2.units)
    note = warn_small_volume(v_stock, "Stock volume")
    return StockResult(v_stock=v_stock, v_diluent=v_dil, note=note)


def calc_serial_dilution(ratio: float, steps: int, vfinal: pint.Quantity) -> pd.DataFrame:
    """
    For each tube:
      sample volume = vfinal/ratio
      diluent volume = vfinal - sample volume
    Cumulative dilution factor: ratio^step
    """
    ensure_positive(vfinal, "Final volume per tube")
    sample = (vfinal / ratio).to(vfinal.units)
    diluent = (vfinal - sample).to(vfinal.units)

    rows: List[dict] = []
    for i in range(1, steps + 1):
        rows.append(
            {
                "Tube": i,
                "Step dilution": f"1:{ratio:g}",
                "Cumulative dilution": f"1:{(ratio ** i):g}",
                "Transfer (sample) volume": format_volume(sample),
                "Diluent volume": format_volume(diluent),
                "Final tube volume": format_volume(vfinal),
            }
        )
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class MolarityResult:
    grams: pint.Quantity


def calc_grams_for_molar_solution(mw_g_per_mol: float, molarity: pint.Quantity, volume: pint.Quantity) -> MolarityResult:
    """grams = M (mol/L) * V (L) * MW (g/mol)"""
    if mw_g_per_mol <= 0:
        raise typer.BadParameter("MW must be > 0 (g/mol).")

    ensure_positive(molarity, "Molarity")
    ensure_positive(volume, "Volume")

    try:
        M = molarity.to(ureg.mol / ureg.L)
    except Exception as e:
        raise typer.BadParameter("Molarity must be like '1 M', '50 mM', '200 uM'.") from e

    try:
        V = volume.to(ureg.L)
    except Exception as e:
        raise typer.BadParameter("Volume must be like '100 mL', '1 L', '500 uL'.") from e

    grams = (M * V * (mw_g_per_mol * ureg.g / ureg.mol)).to(ureg.g)
    return MolarityResult(grams=grams)


@dataclass(frozen=True)
class PercentResult:
    solute_amount: pint.Quantity  # grams for w/v, mL for v/v
    diluent_volume: pint.Quantity  # final_volume - solute_volume (only meaningful for v/v)
    note: str


def calc_percent_solution(kind: str, percent: float, final_volume: pint.Quantity) -> PercentResult:
    """
    w/v: X% w/v = X g per 100 mL final solution
         grams = (percent/100) * (final_volume in mL)

    v/v: X% v/v = X mL solute per 100 mL final solution
         solute_mL = (percent/100) * (final_volume in mL)
         diluent = final_volume - solute_mL
    """
    ensure_positive(final_volume, "Final volume")
    try:
        Vml = final_volume.to(ureg.mL)
    except Exception as e:
        raise typer.BadParameter("Final volume must be a volume like '100 mL' or '1 L'.") from e

    if kind == "wv":
        grams = (percent / 100.0) * Vml.magnitude * ureg.g
        note = "w/v means grams of solute per 100 mL final solution. Add solvent to reach final volume."
        return PercentResult(solute_amount=grams.to(ureg.g), diluent_volume=0 * ureg.mL, note=note)

    if kind == "vv":
        solute = (percent / 100.0) * Vml.magnitude * ureg.mL
        diluent = (Vml - solute).to(ureg.mL)
        note = "v/v means mL of solute per 100 mL final solution. Measure solute, then add diluent up to final volume."
        return PercentResult(solute_amount=solute.to(ureg.mL), diluent_volume=diluent, note=note)

    raise typer.BadParameter("kind must be 'wv' or 'vv'.")


# -------------------------
# Excel export
# -------------------------
def export_excel_single_sheet(df: pd.DataFrame, path: str, sheet_name: str) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)


# -------------------------
# CLI commands
# -------------------------
@app.command()
def dilute(
    c1: str = typer.Option(..., help="Stock concentration, e.g. '10 mM'"),
    c2: str = typer.Option(..., help="Target concentration, e.g. '1 mM'"),
    v2: str = typer.Option(..., help="Final volume, e.g. '50 mL'"),
    export: Optional[str] = typer.Option(None, help="Export results to an Excel file (e.g., dilution.xlsx)"),
):
    """Single dilution using C1V1=C2V2."""
    _ = DilutionInput(c1=c1, c2=c2, v2=v2)

    C1 = q(c1)
    C2 = q(c2)
    V2 = q(v2)

    res = calc_dilution(C1, C2, V2)

    typer.echo("Result (C1V1=C2V2)")
    typer.echo(f"  Stock volume (V1):    {format_volume(res.v1)}")
    typer.echo(f"  Diluent volume:       {format_volume(res.v_diluent)}")
    typer.echo(f"  Final volume (V2):    {format_volume(V2)}")
    if res.note:
        typer.echo(f"  {res.note}")

    df = pd.DataFrame(
        [
            {
                "C1": str(C1),
                "C2": str(C2),
                "V2": str(V2),
                "V1 (stock volume)": format_volume(res.v1),
                "Diluent volume": format_volume(res.v_diluent),
                "Note": res.note or "",
            }
        ]
    )
    if export:
        export_excel_single_sheet(df, export, "dilution")
        typer.echo(f"Exported: {export}")


@app.command("stock-to-working")
def stock_to_working(
    stock: str = typer.Option(..., help="Stock factor, e.g. '10X'"),
    final: str = typer.Option("1X", help="Final factor, usually '1X'"),
    v2: str = typer.Option(..., help="Final volume, e.g. '500 mL'"),
    export: Optional[str] = typer.Option(None, help="Export results to an Excel file (e.g., stock.xlsx)"),
):
    """Make working solution from an X stock."""
    _ = StockInput(stock=stock, final=final, v2=v2)

    stock_x = parse_x_factor(stock)
    final_x = parse_x_factor(final)
    V2 = q(v2)

    res = calc_stock_to_working(stock_x, final_x, V2)

    typer.echo("Result (Stock-to-Working)")
    typer.echo(f"  Stock: {stock_x:g}X -> Final: {final_x:g}X")
    typer.echo(f"  Stock volume:         {format_volume(res.v_stock)}")
    typer.echo(f"  Diluent volume:       {format_volume(res.v_diluent)}")
    typer.echo(f"  Final volume:         {format_volume(V2)}")
    if res.note:
        typer.echo(f"  {res.note}")

    df = pd.DataFrame(
        [
            {
                "Stock": f"{stock_x:g}X",
                "Final": f"{final_x:g}X",
                "Final Volume": str(V2),
                "Stock volume": format_volume(res.v_stock),
                "Diluent volume": format_volume(res.v_diluent),
                "Note": res.note or "",
            }
        ]
    )
    if export:
        export_excel_single_sheet(df, export, "stock_to_working")
        typer.echo(f"Exported: {export}")


@app.command()
def serial(
    ratio: float = typer.Option(..., help="Dilution ratio per step (e.g., 10 for 1:10)"),
    steps: int = typer.Option(..., help="Number of steps (tubes)"),
    vfinal: str = typer.Option(..., help="Final volume per tube, e.g. '1 mL'"),
    export: Optional[str] = typer.Option(None, help="Export results to an Excel file (e.g., serial.xlsx)"),
):
    """Serial dilution table (same final volume each tube)."""
    _ = SerialInput(ratio=ratio, steps=steps, vfinal=vfinal)
    Vfinal = q(vfinal)

    df = calc_serial_dilution(ratio=ratio, steps=steps, vfinal=Vfinal)

    typer.echo("Serial dilution table:")
    typer.echo(df.to_string(index=False))

    sample_vol = (Vfinal / ratio).to(Vfinal.units)
    note = warn_small_volume(sample_vol, "Transfer volume per step")
    if note:
        typer.echo(note)

    if export:
        export_excel_single_sheet(df, export, "serial_dilution")
        typer.echo(f"Exported: {export}")


@app.command()
def molarity(
    mw: float = typer.Option(..., help="Molecular weight in g/mol (e.g., 121.14)"),
    molarity: str = typer.Option(..., help="Target concentration (e.g., '1 M', '50 mM')"),
    volume: str = typer.Option(..., help="Final volume (e.g., '100 mL', '1 L')"),
    export: Optional[str] = typer.Option(None, help="Export results to an Excel file (e.g., molarity.xlsx)"),
):
    """Calculate grams of solute needed for a target molarity and volume."""
    _ = MolarityInput(mw=mw, molarity=molarity, volume=volume)

    M = q(molarity)
    V = q(volume)

    res = calc_grams_for_molar_solution(mw, M, V)

    typer.echo("Result (Molarity from powder)")
    typer.echo(f"  MW:                 {mw:g} g/mol")
    typer.echo(f"  Target molarity:    {str(M)}")
    typer.echo(f"  Final volume:       {str(V)}")
    typer.echo(f"  Grams required:     {res.grams.magnitude:.6g} g")

    df = pd.DataFrame(
        [
            {
                "MW (g/mol)": mw,
                "Target molarity": str(M),
                "Final volume": str(V),
                "Grams required (g)": float(res.grams.magnitude),
                "Notes": "Weigh solute, add ~80% solvent, dissolve, then bring to final volume.",
            }
        ]
    )

    if export:
        export_excel_single_sheet(df, export, "molarity")
        typer.echo(f"Exported: {export}")


@app.command()
def percent(
    kind: str = typer.Option(..., help="wv (w/v) or vv (v/v)"),
    percent: float = typer.Option(..., help="Percent value (0-100)"),
    final_volume: str = typer.Option(..., help="Final volume (e.g., '100 mL', '500 mL')"),
    export: Optional[str] = typer.Option(None, help="Export results to an Excel file (e.g., percent.xlsx)"),
):
    """
    Percent solutions:
      - wv: % (w/v) = grams per 100 mL final solution
      - vv: % (v/v) = mL per 100 mL final solution
    """
    kind_clean = kind.strip().lower()
    _ = PercentInput(kind=kind_clean, percent=percent, final_volume=final_volume)

    V = q(final_volume)
    res = calc_percent_solution(kind_clean, percent, V)

    typer.echo("Result (Percent solution)")
    typer.echo(f"  Type:               {kind_clean}")
    typer.echo(f"  Percent:            {percent:g}%")
    typer.echo(f"  Final volume:       {format_volume(V)}")

    if kind_clean == "wv":
        typer.echo(f"  Solute required:    {res.solute_amount.magnitude:.6g} g")
        typer.echo(f"  Note:               {res.note}")

        df = pd.DataFrame(
            [
                {
                    "Type": "w/v",
                    "Percent": percent,
                    "Final volume": str(V),
                    "Solute required (g)": float(res.solute_amount.to(ureg.g).magnitude),
                    "Note": res.note,
                }
            ]
        )

    else:  # vv
        typer.echo(f"  Solute volume:      {format_volume(res.solute_amount)}")
        typer.echo(f"  Diluent volume:     {format_volume(res.diluent_volume)}")
        typer.echo(f"  Note:               {res.note}")

        df = pd.DataFrame(
            [
                {
                    "Type": "v/v",
                    "Percent": percent,
                    "Final volume": str(V),
                    "Solute volume (mL)": float(res.solute_amount.to(ureg.mL).magnitude),
                    "Diluent volume (mL)": float(res.diluent_volume.to(ureg.mL).magnitude),
                    "Note": res.note,
                }
            ]
        )

    if export:
        export_excel_single_sheet(df, export, "percent")
        typer.echo(f"Exported: {export}")


if __name__ == "__main__":
    app()
