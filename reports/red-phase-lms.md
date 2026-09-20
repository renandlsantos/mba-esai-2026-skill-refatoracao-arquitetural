# LMS red phase

The new factory tests failed because the baseline did not export createApp. Importing its app.js also started its unguarded port3000 listener; the owned process was immediately stopped after about eight seconds. Database was synthetic in-memory data. Root cause: unconditional app.listen at module import. The refactor separates factory/export from require.main boot and binds 127.0.0.1 only. Earlier safe baseline harness bypassed this entry point and exercised all three routes on loopback. No retry of the unguarded baseline import occurred.
