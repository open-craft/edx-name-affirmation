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
[0.8.2] - 2021-08-31
~~~~~~~~~~~~~~~~~~~~
* Update django admin to allow editing of VerifiedName and VerifiedNameConfig

[0.8.1] - 2021-08-30
~~~~~~~~~~~~~~~~~~~~
* Emit signal when `VerifiedName` status changes to "approved".

[0.8.0] - 2021-08-30
~~~~~~~~~~~~~~~~~~~~
* Add signal receivers for IDV and proctoring attempts

[0.7.0] - 2021-08-26
~~~~~~~~~~~~~~~~~~~~
* Add verified_name_enabled and use_verified_name_for_certs to the GET response of VerifiedNameHistoryView.

[0.6.4] - 2021-08-18
~~~~~~~~~~~~~~~~~~~~
* Remove verified name is_verified from DB

[0.6.3] - 2021-08-18
~~~~~~~~~~~~~~~~~~~~
* Update admin for verified name status

[0.6.2] - 2021-08-17
~~~~~~~~~~~~~~~~~~~~
* Remove verified name is_verified from model

[0.6.1] - 2021-08-17
~~~~~~~~~~~~~~~~~~~~
* Django settings updates for admin app

[0.6.0] - 2021-08-11
~~~~~~~~~~~~~~~~~~~~
* Add name verification status field, replacing single is_verified boolean.

[0.5.0] - 2021-08-11
~~~~~~~~~~~~~~~~~~~~
* Add API method and endpoint to return a complete list of the user's
  VerifiedNames, ordered by most recently created.

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
