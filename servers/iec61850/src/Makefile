LIBIEC_HOME=../libs/libiec61850/

PROJECT_BINARY_NAME = iec61850
PROJECT_SOURCES = custom-ied.c
PROJECT_SOURCES += static_model.c

include $(LIBIEC_HOME)/make/target_system.mk
include $(LIBIEC_HOME)/make/stack_includes.mk

all:	libs $(PROJECT_BINARY_NAME)

libs:
	make -C $(LIBIEC_HOME)

include $(LIBIEC_HOME)/make/common_targets.mk

LDLIBS += -lm

CP = cp

model:	$(PROJECT_ICD_FILE)
	java -jar $(LIBIEC_HOME)/tools/model_generator/genmodel.jar $(PROJECT_ICD_FILE)

$(PROJECT_BINARY_NAME):	$(PROJECT_SOURCES) $(LIB_NAME)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(PROJECT_BINARY_NAME) $(PROJECT_SOURCES) $(INCLUDES) $(LIB_NAME) $(LDLIBS)

clean:
	rm -f $(PROJECT_BINARY_NAME)
