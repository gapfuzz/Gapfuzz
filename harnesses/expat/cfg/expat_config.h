/* gapfuzz용 최소 expat 설정 (Linux x86-64). OSS-Fuzz의 cmake 빌드와 같은 기능을 켠다. */
#ifndef EXPAT_CONFIG_H
#define EXPAT_CONFIG_H 1
#define BYTEORDER 1234
#define HAVE_FCNTL_H 1
#define HAVE_GETPAGESIZE 1
#define HAVE_GETRANDOM 1
#define HAVE_SYSCALL_GETRANDOM 1
#define HAVE_INTTYPES_H 1
#define HAVE_MMAP 1
#define HAVE_STDINT_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRING_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_SYS_TYPES_H 1
#define HAVE_UNISTD_H 1
#define PACKAGE "expat"
#define PACKAGE_URL ""
#define STDC_HEADERS 1
#define XML_CONTEXT_BYTES 1024
#define XML_DEV_URANDOM 1
#define XML_DTD 1
#define XML_GE 1
#define XML_NS 1
#endif
