Change Log
----------

..
   All enhancements and patches to edx-name-affirmation will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[0.4.0] - 2021-08-06
~~~~~~~~~~~~~~~~~~~~
* Expose API methods through `NameAffirmationService`.

[0.3.1] - 2021-08-03
~~~~~~~~~~~~~~~~~~~~
* Update `MANIFEST.in` to include all directories under `edx_name_affirmation`.

[0.3.0] - 2021-08-02
~~~~~~~~~~~~~~~~~~~~
* Add `use_verified_name_for_certs` field to the VerifiedNameView
  response, and create a new endpoint to update the user's verified
  name config.
* Admin page configuration for VerifiedName and VerifiedNameConfig.

[0.2.0] - 2021-07-22
~~~~~~~~~~~~~~~~~~~~
* Add verified_name_enabled to VerifiedNameView GET response.
* Add PR template.
* Add VerifiedNameConfig model and API functions.

[0.1.2] - 2021-07-02
~~~~~~~~~~~~~~~~~~~~
* Add plugin support.

[0.1.1] - 2021-06-30
~~~~~~~~~~~~~~~~~~~~
* Fix typo in publish-pypi job.

[0.1.0] - 2021-06-30
~~~~~~~~~~~~~~~~~~~~
* Initialize project along with `VerifiedName` model, Python API, and REST endpoints.
