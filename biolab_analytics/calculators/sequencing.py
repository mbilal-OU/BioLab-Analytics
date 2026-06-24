
def genome_coverage(read_count, read_length_bp, genome_size_bp):
    if read_count <= 0 or read_length_bp <= 0 or genome_size_bp <= 0:
        raise ValueError("All values must be positive.")
    return read_count * read_length_bp / genome_size_bp

def reads_required(target_coverage, read_length_bp, genome_size_bp):
    if target_coverage <= 0 or read_length_bp <= 0 or genome_size_bp <= 0:
        raise ValueError("All values must be positive.")
    return target_coverage * genome_size_bp / read_length_bp
