#!/usr/bin/env bash
# Script to clone, move, set permissions, and run ICAMS download

# Exit immediately if a command fails
set -e

# 1. Clone the repository
git clone https://github.com/alejobeap/Icams_files.git

# 2. Move all files from the cloned repo to the current directory
mv Icams_files/* .

# 3. Remove the now-empty cloned directory
rm -rf Icams_files

# 4. Make all shell scripts executable
chmod 777 *.sh

# 5. Run the main script
./descargar_icam_fromjobs_new.sh
