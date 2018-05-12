#undef TRACEPOINT_PROVIDER
#define TRACEPOINT_PROVIDER hypergraph

#undef TRACEPOINT_INCLUDE
#define TRACEPOINT_INCLUDE "./hypergraph.h"

#if !defined(_HYPERGRAPH_H) || defined(TRACE_HEADER_MULTI_READ)
#define _HYPERGRAPH_H

#include <linux/tracepoint.h>

TRACEPOINT_EVENT(hypergraph, hypergraph_host,
	TP_PROTO(unsigned long nr),
	TP_ARGS(nr),
	TP_FIELDS(
		ctf_integer(unsigned long, nr, nr)
	)
)


#endif /* _HYPERGRAPH_H */

/* This part must be outside protection */
// #include <linux/tracepoint-event.h>
/* Make all open coded DECLARE_TRACE nops */
#undef DECLARE_TRACE
#define DECLARE_TRACE(name, proto, args)