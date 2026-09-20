# Task Manager red phase

The regression suite deliberately refused to import the baseline because it lacked create_app and performed db.create_all at import. This isolated failure was expected; the earlier copied baseline exercised all22 routes and confirmed password-hash exposure/fake tokens. Factory and separation were implemented before retry.
