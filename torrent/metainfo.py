import hashlib
import bisect

from bcoding import bencode


# ---------------------------------------- #
# http://bittorrent.org/beps/bep_0003.html #
# ---------------------------------------- #

# <h1>metainfo files</h1>

# <p>Metainfo files (also known as .torrent files) are bencoded dictionaries with the following keys:</p>


# The URL of the tracker.
def get_announce(decoded: dict) -> str:
	return decoded['announce']


# This maps to a dictionary, with keys described below.
def get_info(decoded: dict) -> dict:
	return decoded['info']


# <h2>info dictionary</h2>


# The `name` key maps to a UTF-8 encoded string which is the suggested name to
# save the file (or directory) as. It is purely advisory.
def get_name(decoded: dict) -> str:
	return decoded['info']['name']


# `piece length` maps to the number of bytes in each piece the file is split into.
# For the purposes of transfer, files are split into fixed-size pieces which are
# all the same length except for possibly the last one which may be truncated.
# `piece length` is almost always a power of two, most commonly 2 18 = 256 K
# (BitTorrent prior to version 3.2 uses 2 20 = 1 M as default).
def get_piece_length(decoded: dict) -> int:
	return decoded['info']['piece length']


# `pieces` maps to a string whose length is a multiple of 20. It is to be subdivided
# into strings of length 20, each of which is the SHA1 hash of the piece at the corresponding index.
def get_pieces(decoded: dict) -> list[str]:
	pieces = []
	pieces_raw = decoded['info']['pieces']
	pieces_num = int(len(pieces_raw) / 20)
	for i in range(pieces_num):
		pieces.append(pieces_raw[i * 20:(i + 1) * 20])
	return pieces


# <p>There is also a key `length` or a key `files`, but not both or neither.
# If `length` is present then the download represents a single file,
# otherwise it represents a set of files which go in a directory structure.</p>


# In the single file case, length maps to the length of the file in bytes.
def get_length(decoded: dict) -> int:
	return decoded['info']['length']


# For the purposes of the other keys, the multi-file case is treated as only having a single file by concatenating
# the files in the order they appear in the files list. The files list is the value files maps to,
# and is a list of dictionaries containing the following keys:
# 
# `length` - The length of the file, in bytes.
# 
# `path` - A list of UTF-8 encoded strings corresponding to subdirectory names,
# the last of which is the actual file name (a zero length list is an error case).


def get_files(decoded: dict) -> list[tuple[int, str]]:
	return [(i['length'], i['path']) for i in decoded['info']['files']]


# The 20 byte sha1 hash of the bencoded form of the info value from the metainfo file.
# This value will almost certainly have to be escaped.
# 
# Note that this is a substring of the metainfo file. The info-hash must be the hash of the encoded form
# as found in the .torrent file, which is identical to bdecoding the metainfo file, extracting the info
# dictionary and encoding it if and only if the bdecoder fully validated the input (e.g. key ordering,
# absence of leading zeros). Conversely that means clients must either reject invalid metainfo files or
# extract the substring directly. They must not perform a decode-encode roundtrip on invalid data.


def get_infohash_sha1_digest(decoded: dict) -> bytes:
	info = bencode(decoded["info"])
	# Returns the digest (i.e., the series of raw bytes representing the hash). This is 20 bytes long.
	return hashlib.sha1(info).digest()


def get_infohash_sha1_hexdigest(decoded: dict) -> str:
	info = bencode(decoded["info"])
	# returns the hexdigest (i.e., a UTF8 hexadecimal encoding of the raw bytes). This is 40 characters long.
	return hashlib.sha1(info).hexdigest()


# ---------------------------------------- #
# Validation                               #
# ---------------------------------------- #


def validate_v1_metainfo(decoded: dict) -> bool:
	# metainfo file must contain all of the following attributes:
	try:
		get_announce(decoded)
		get_name(decoded)
		get_piece_length(decoded)
		get_pieces(decoded)
	except KeyError:
		return False
	
	# metainfo file must contain only one of the following attributes:
	try:
		get_length(decoded)
	except KeyError:
		length_present = False
	else:
		length_present = True
	
	try:
		get_files(decoded)
	except KeyError:
		files_present = False
	else:
		files_present = True
	
	return length_present != files_present


# ---------------------------------------- #
# Utility                                  #
# ---------------------------------------- #


def get_torrent_size(decoded: dict) -> int:
	try:
		size = sum(i[0] for i in get_files(decoded))
	except KeyError:
		size = get_length(decoded)
	
	return size


# Returns a dictionary with keys being directory names and values being dictionaries.
# Key names equal to './' instead contain a list of tuples of file names plus file sizes.
def get_torrent_file_listing(decoded: dict) -> dict[str, dict]:
	name = get_name(decoded)
	
	tree = { }
	
	try:
		files = get_files(decoded)
		root = tree.setdefault(name, { }) # for a multi-file torrent, create the root directory
	except KeyError:
		files = [(get_length(decoded), [name])]
		root = tree # for a single-file torrent, we don't need a special root directory
	
	for (size, path_segments) in files:
		if len(path_segments) == 1: # if the file isn't contained under any directories:
			bisect.insort_left(root.setdefault('./', []), (path_segments[0], size))
		else: # else, we have a list of directories and then the filename at the end:
			node = root # reset `node`, which keeps track of the deepest directory we've travelled to so far
			
			# For every directory in the list:
			# 
			# Create a new entry in the dictionary pointed to by `node`,
			#   with the key being the directory name, and the value being an empty dictionary.
			# 
			# Finally, assign `node` to said value.
			for segment in path_segments[0:-1]:
				node.setdefault(segment, { })
				node = node[segment]
			
			# After the loop has finished, `node` points to the final directory that contains the file.
			bisect.insort_left(node.setdefault('./', []), (path_segments[-1], size))
	
	return tree
