#include "iec61850_server.h"
#include "hal_thread.h"
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include "static_model.h"

/* import IEC 61850 device model created from SCL-File */
extern IedModel iedModel;

static int running = 0;
static IedServer iedServer = NULL;

void sigint_handler(int signalId)
{
  running = 0;
}

static void
connectionHandler(IedServer self, ClientConnection connection,
      bool connected, void *parameter)
{
  if (connected)
    printf("Connection opened\n");
  else
    printf("Connection closed\n");
}


static MmsError
fileAccessHandler(void *parameter, MmsServerConnection connection,
      MmsFileServiceType service, const char *localFilename,
      const char *otherFilename)
{
  // TODO: More informative output
  printf
      ("fileAccessHandler: service = %i, local-file: %s other-file: %s\n",
       service, localFilename, otherFilename);

  /* Don't allow client to rename files */
  if (service == MMS_FILE_ACCESS_TYPE_RENAME)
    return MMS_ERROR_FILE_FILE_ACCESS_DENIED;

  /* Don't allow client to delete files */
  if (service == MMS_FILE_ACCESS_TYPE_DELETE) {
    return MMS_ERROR_FILE_FILE_ACCESS_DENIED;
  }

  /* allow all other accesses */
  return MMS_ERROR_NONE;
}



int main(int argc, char **argv)
{
  /* MMS server will be instructed to start listening for client connections. */
  int tcpPort = 102;
  if (argc > 1)
    tcpPort = atoi(argv[1]);

  char *filesdir = NULL;
  if (argc > 2)
    filesdir = argv[2];

  printf("Using libIEC61850 version %s\n", LibIEC61850_getVersionString());

  /* Create new server configuration object */
  IedServerConfig config = IedServerConfig_create();

  /* Set buffer size for buffered report control blocks to 200000 bytes */
  IedServerConfig_setReportBufferSize(config, 200000);

  /* Set stack compliance to a specific edition of the standard (WARNING: data model has also to be checked for compliance) */
  IedServerConfig_setEdition(config, IEC_61850_EDITION_2);

  /* Set the base path for the MMS file services */
  if (filesdir != NULL) {
    IedServerConfig_setFileServiceBasePath(config, filesdir);
    /* enable MMS file service */
    IedServerConfig_enableFileService(config, true);
  } else {
    IedServerConfig_setFileServiceBasePath(config, "./tmp/");
    /* enable MMS file service */
    IedServerConfig_enableFileService(config, false);
  }


  /* enable dynamic data set service */
  IedServerConfig_enableDynamicDataSetService(config, true);

  /* disable log service */
  IedServerConfig_enableLogService(config, false);

  /* set maximum number of clients */
  IedServerConfig_setMaxMmsConnections(config, 5);

  /* Create a new IEC 61850 server instance */
  iedServer = IedServer_createWithConfig(&iedModel, NULL, config);

  /* configuration object is no longer required */
  IedServerConfig_destroy(config);

  /* set the identity values for MMS identify service */
  IedServer_setServerIdentity(iedServer, "Cappy", "custom ied", "0.1");

  IedServer_setConnectionIndicationHandler(iedServer,
             (IedConnectionIndicationHandler)
             connectionHandler, NULL);

  /* By default access to variables with FC=DC and FC=CF is not allowed.
   * This allow to write to simpleIOGenericIO/GGIO1.NamPlt.vendor variable used
   * by iec61850_client_example1.
   */
  IedServer_setWriteAccessPolicy(iedServer, IEC61850_FC_DC,
         ACCESS_POLICY_ALLOW);

  if (filesdir != NULL) {
    /* Set a callback handler to control file accesses */
    MmsServer mmsServer = IedServer_getMmsServer(iedServer);
    MmsServer_installFileAccessHandler(mmsServer, fileAccessHandler, NULL);
  }

  IedServer_start(iedServer, tcpPort);

  if (!IedServer_isRunning(iedServer)) {
    printf
  ("Starting server failed (maybe need root permissions or another server is already using the port)! Exit.\n");
    IedServer_destroy(iedServer);
    exit(-1);
  }

  running = 1;

  signal(SIGINT, sigint_handler);

  float t = 0.f;
  uint64_t last_timestamp = Hal_getTimeInMs();

  while (running) {
    uint64_t timestamp = Hal_getTimeInMs();

    t += 0.1f;

    float an1 = sinf(t);
    float an2 = sinf(t + 1.f);
    float an3 = sinf(t + 2.f);
    float an4 = sinf(t + 3.f);

    Timestamp iecTimestamp;

    Timestamp_clearFlags(&iecTimestamp);
    Timestamp_setTimeInMilliseconds(&iecTimestamp, timestamp);
    Timestamp_setLeapSecondKnown(&iecTimestamp, true);

    /* toggle clock-not-synchronized flag in timestamp */
    if (((int) t % 2) == 0)
      Timestamp_setClockNotSynchronized(&iecTimestamp, true);

    Thread_sleep(100);
  }

  /* stop MMS server - close TCP server socket and all client sockets */
  IedServer_stop(iedServer);

  /* Cleanup - free all resources */
  IedServer_destroy(iedServer);

  return 0;
}        /* main() */
