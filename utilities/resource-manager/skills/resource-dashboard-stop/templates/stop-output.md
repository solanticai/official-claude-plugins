{{#if graceful}}Dashboard on port {{port}} stopped.{{/if}}
{{#if pidfile_kill}}Dashboard (pid {{pid}}) stopped via pid-file.{{/if}}
{{#if no_op}}No dashboard running on port {{port}}.{{/if}}
