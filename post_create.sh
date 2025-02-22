# #!/usr/bin/env bash

# workspace=/workspaces/file_saver

# # Install Maturin if not already installed, alias python3 to python so we don't have to type the 3 (save so much time, wow!) and,
# # install the developed package.
# install_rust_lib () {
#     echo "Installing: Python libraries written in Rust"
#     cargo install maturin && \
#     # cat ~/.zshrc | grep -q 'alias python python3' || echo "alias python python3" >> ~/.zshrc && \
#     # bash /workspaces/file_saver/rebuild_rust.sh
#     maturin develop
# }

# # Logic check to make sure we're in the right directory to build the rust library
# if [ ./ -ef "./file_saver_rust" ]; then 
#     install_rust_lib
# else
#     cd $workspace/file_saver_rust
#     install_rust_lib
# fi

# Setup UV
uv sync
