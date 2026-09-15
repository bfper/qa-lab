# E2E — weeks 2 and 3

Week 2: three tests against mentoria login — valid, wrong password, empty
field. Record with `playwright codegen http://localhost:18002`, then rewrite
by hand with `get_by_role`. Comparing the two is the lesson.

Rules from day one:
- web-first assertions only: `expect(locator).to_be_visible()`, never
  `assert locator.is_visible()`
- no `page.wait_for_timeout` anywhere in the suite
- break a selector on purpose, run with `--tracing=retain-on-failure`,
  open it with `playwright show-trace`

Week 3: `storage_state` for two roles (mentor, mentorando), data seeded via
`APIRequestContext` and torn down in the fixture, Page Objects, suite stable
across five consecutive runs.
