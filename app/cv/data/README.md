# CV data

`sample_profiles.json` holds twelve fictional profiles. Every person, employer,
certificate and id in it is invented, so it is safe to publish and to demo.

To index a different set of profiles, point `CV_SNAPSHOT_PATH` at a JSON file with
the same shape (see `app/cv/models/cv_snapshot.py`) and call `POST /cv/reindex`.
Keep real CV data outside this repository.
