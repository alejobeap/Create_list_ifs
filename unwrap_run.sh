


parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")


bsub2slurm.sh -o sbatch_logs/"UNW_${parent_dir}\_${current_dir}".out -e sbatch_logs/"UNW_${parent_dir}\_${current_dir}".err -J "UNW_${parent_dir}\_${current_dir}" -n 10 -W 4
7:59 -M 81620 -q comet ./unwrap_sin_png_from_list.sh
