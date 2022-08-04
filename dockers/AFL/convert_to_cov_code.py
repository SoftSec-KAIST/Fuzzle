import sys

code = sys.argv[1]

f = open(code + '.c', 'r')
cov_code = f.read().replace('abort();','__gcov_flush();\n\tabort();')
f.close()

f_cov = open(code + '_cov.c', 'w')
f_cov.write(cov_code)
f_cov.close()