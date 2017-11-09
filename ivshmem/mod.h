#include <linux/proc_fs.h>
#include <linux/tracepoint.h>

typedef void (*set_tp_func_t)(struct tracepoint *tp, void *priv);

struct tracepoint_entry {
	void *probe;
	void *data;
	const char *name;
	struct tracepoint *tp;	
};

struct tracepoint_entries {
	int size;
	struct tracepoint_entry *entries;
};

static int tracing_enabled;

inline int is_tracing_enabled(void) {
	return tracing_enabled;
}
/*
 * pseudo filesystem interface
 */
ssize_t mod_write(struct file *filp, const char __user *ubuf,
			size_t cnt, loff_t *ppos)
{
	unsigned long val;
	int ret;

	ret = kstrtoul_from_user(ubuf, cnt, 10, &val);
	if (ret)
		return ret;

	tracing_enabled = val != 0;
	*ppos += cnt;
	return cnt;
}

ssize_t mod_read(struct file *f, char *buf, size_t size, loff_t *offset)
{
	int n;
    char output[255]; /* More than enough to hold UINT_MAX + "\n"*/
	n = sprintf(output, "tracing_on: %d\n", tracing_enabled);

    return simple_read_from_buffer(buf, size, offset, output, n);
}

int mod_tracepoint_probe_register(struct tracepoint_entry *entry)
{
	int ret = 0;

	if(entry->tp == NULL){
		printk("register %s hooks failed, tracepoint not found\n", entry->name);
		return -EINVAL;
	}

	ret = tracepoint_probe_register(entry->tp, entry->probe, entry->data);
	if(ret){
		printk("register %s hooks failed ret=%d\n", entry->name, ret);
		tracepoint_probe_unregister(entry->tp, entry->probe, entry->data);
		return ret;
	}

	printk("tracepoint found: %p %s\n", entry->tp,
		entry->tp ? entry->tp->name : "null");
	return ret;
}

void mod_tracepoint_probe_unregister(struct tracepoint_entry *entry)
{
	if(entry == NULL)
		return;
	if(entry->tp == NULL || entry->probe == NULL)
		return;

	printk("%s probe was unregistered\n", entry->name);
	tracepoint_probe_unregister(entry->tp, entry->probe, entry->data);
}

static int mod_tracepoint_coming(struct tp_module *tp_mod, 
	set_tp_func_t set_tracepoint, void *priv)
{
	int i, ret = 0;

	for (i = 0; i < tp_mod->mod->num_tracepoints; i++) {
		struct tracepoint *tp = tp_mod->mod->tracepoints_ptrs[i];

		if (set_tracepoint)
			set_tracepoint(tp, priv);
	}
	return ret;
}

static void set_tracepoint(struct tracepoint *tp, void *priv)
{
	struct tracepoint_entries *tp_entries = priv;
	int i;
	if(!tp_entries)
		return;

	for(i = 0; i < tp_entries->size; i++) {
		if (strcmp(tp->name, tp_entries->entries[i].name) == 0 
			/*&& tracepoint_table[j].tp == NULL*/) {
			tp_entries->entries[i].tp = tp;
			mod_tracepoint_probe_register(&tp_entries->entries[i]);
		}
	}
}

static void unregister_all_probes(struct tracepoint_entries *tp_entries)
{
	int i;
	for(i = 0; i < tp_entries->size; i++)
		mod_tracepoint_probe_unregister(&tp_entries->entries[i]);
}