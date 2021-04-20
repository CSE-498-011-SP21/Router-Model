# Router-Model

## Test workload generator (gen directory)
Install numpy if not installed
```
pip install numpy
```

To run with default arguments, run
```
python3 generate.py
```

Usage with command line arguments
```
usage: generate.py [-h] [-l LENGTH] [-s SKEW] [-a ALPHA] [-o OUTFILE]
-l LENGTH, --length LENGTH  length of the request stream
-s SKEW, --skew SKEW  ratio of gets in the stream
-a ALPHA, --alpha ALPHA  Zipfian alpha value (a > 1)
-o OUTFILE, --outfile OUTFILE  name of the output file ([outfile].csv)
```