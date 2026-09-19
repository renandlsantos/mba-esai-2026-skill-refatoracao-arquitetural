# Target MVC responsibilities

Models express domain data/invariants; repositories own queries and persistence. Controllers coordinate a use case and transaction/side-effect sequence, accepting validated domain inputs rather than global transport state. Views serialize public output; API routes adapt HTTP requests/results, status codes and headers. API MVC can have JSON views rather than templates.

Dependencies flow from routes into controllers and model/repository interfaces. Composition root constructs configuration, repositories, controllers, routes and error handlers. Inject collaborators that enable meaningful isolation (database/payment/clock); do not create interfaces for every trivial function. Keep framework-specific boot code out of business rules.

Configuration comes from explicit environment or caller-provided settings. No fixed credentials, debug mode or all-interface bind as defaults. Initialization must not overwrite populated data. Close/teardown connections with clear ownership. A transaction belongs to one complete use case, and tests prove rollback on intermediate failure.

Use parameterized queries/ORM expressions; allowlist any dynamic identifier. Keep passwords, hashes, internal exceptions and infrastructure secrets out of public serializers/logs. Validate the complete update before mutating tracked models. Centralize stable error-to-HTTP mapping and retain framework 404/405 semantics.

Do not add production identity management merely to draw MVC folders. If an existing privileged endpoint is unsafe, propose the smallest explicit guard and document its contract. Broader access-control requirements need a separate decision. Preserve useful layers in partially organized projects; migrate incrementally and validate data compatibility.
