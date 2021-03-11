import zstandard

# use zstd to decompress the input stream
# the example streams are not compressed (csv), so this is not needed yet

with open('cluster001', 'rb') as fh:
	dctx = zstandard.ZstdDecompressor()
	reader = dctx.stream_reader(fh)
	chunk = reader.read(16384)
	print(chunk)
