#include <babeltrace/ctf-writer/writer.h>
#include <babeltrace/ctf-writer/clock.h>
#include <babeltrace/ctf-writer/stream.h>
#include <babeltrace/ctf-writer/event.h>
#include <babeltrace/ctf-writer/event-types.h>
#include <babeltrace/ctf-writer/event-fields.h>
#include <babeltrace/ctf-writer/stream-class.h>
// #include <babeltrace/ctf-ir/packet.h>
// #include <babeltrace/ref.h>
#include <babeltrace/ctf/events.h>
// #include <babeltrace/values.h>

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <sys/stat.h>

/* support babeltrace 1.5 and + */
void main()
{
    static char trace_path[] = "/tmp/ctfwriter_XXX";
    char metadata_path[sizeof(trace_path) + 9];
    const char *clock_name = "test_clock";
	const char *clock_description = "This is a test clock";
    static struct bt_ctf_trace *trace;
    static struct bt_ctf_writer *writer = NULL;
    struct bt_ctf_clock *clock;
    int64_t get_offset_s, get_offset, get_time;
    struct bt_ctf_stream_class *stream_class;
    struct bt_ctf_stream *stream1;
    int64_t current_time = 42;

    strcpy(metadata_path, trace_path);
	strcat(metadata_path + sizeof(trace_path) - 1, "/metadata");
    printf("Traces will be written at %s\n", trace_path);
    /* create writer */
    writer = bt_ctf_writer_create(trace_path);
    // trace = bt_ctf_writer_get_trace(writer);
    bt_ctf_writer_add_environment_field(writer, "host", "abder");

    /* create clock */
    clock = bt_ctf_clock_create(clock_name);
    // bt_ctf_clock_set_time(clock, current_time);
    bt_ctf_clock_set_description(clock, clock_description);
    // printf("Clock description is %s\n", bt_ctf_clock_get_description(clock));
    // printf("Clock frequency is %d\n", bt_ctf_clock_get_frequency(clock));
    // printf("Clock precision is %d\n", bt_ctf_clock_get_precision(clock));
    // printf("Clock is absolute: %s\n", bt_ctf_clock_get_is_absolute(clock));
    // bt_ctf_clock_get_time(clock, &get_time);
    // printf("Clock time is %d\n", get_time);

    bt_ctf_writer_add_clock(writer, clock);

    /* Define a stream class */
	stream_class = bt_ctf_stream_class_create("test_stream");
    bt_ctf_stream_class_set_clock(stream_class, clock);

    /* create event class */
    struct bt_ctf_event_class *event_class = bt_ctf_event_class_create("SimpleEvent");

    // Create a floating point type
    struct bt_ctf_field_type *float_type = bt_ctf_field_type_floating_point_create();
    bt_ctf_field_type_set_alignment(float_type, 32);
    bt_ctf_field_type_floating_point_set_exponent_digits(float_type, 11);
    bt_ctf_field_type_floating_point_set_mantissa_digits(float_type, 53);

    // event_class.add_field(floating_point_type, "float_field")
    bt_ctf_event_class_add_field(event_class, float_type, "float_field");

    bt_ctf_stream_class_add_event_class(stream_class, event_class);

    /* Instantiate a stream and append events */
    stream1 = bt_ctf_writer_create_stream(writer, stream_class);

    /* create events */
    for(int i = 0; i < 100; i++)
    {
        struct bt_ctf_event *simple_event = bt_ctf_event_create(event_class);
        bt_ctf_clock_set_time(clock, ++current_time);
        struct bt_ctf_field *float_field = bt_ctf_event_get_payload(simple_event, "float_field");
        bt_ctf_field_floating_point_set_value(float_field, (float)i + 0.65);

        /* Append event to stream */
        bt_ctf_stream_append_event(stream1, simple_event);
    }
    /* Flush stream */
    printf("Flushed the stream \n");
    bt_ctf_stream_flush(stream1);

    bt_ctf_writer_flush_metadata(writer);

    free(clock);
	free(writer);
	free(stream1);
    // free(trace);
	free(stream_class);
    free(float_type);
    return;
}