PROTOS = $(wildcard *.proto)
PROTO_COMP = $(patsubst %.proto, %_pb2.py,$(PROTOS))
SRC_DIR = ..
DST_DIR = $(SRC_DIR)/msg

all: $(PROTO_COMP)

%_pb2.py : %.proto
	protoc --python_out=$(DST_DIR) $<
