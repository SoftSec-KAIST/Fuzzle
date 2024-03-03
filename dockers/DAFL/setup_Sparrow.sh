cd /home/maze/
git clone https://github.com/prosyslab/sparrow.git

cd /home/maze/sparrow
git checkout dafl
export OPAMYES=1


sed -i '/^opam init/ s/$/ --disable-sandboxing/' build.sh
./build.sh
opam install ppx_compare yojson ocamlgraph memtrace lymp clangml conf-libclang.12 batteries apron conf-mpfr cil linenoise claml

eval $(opam env)
make clean
make
