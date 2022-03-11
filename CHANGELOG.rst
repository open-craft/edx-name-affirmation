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
[2.3.2] - 2022-03-11
~~~~~~~~~~~~~~~~~~~~
* Add simple_history tracking to the VerifiedName model

[2.3.1] - 2022-03-02
~~~~~~~~~~~~~~~~~~~~
* Add two signal handlers to capture post_delete signals from ProctoredExamStudentAttempt and SoftwareSecurePhotoVerification models.
  If those signals are received, the corresponding VerifiedName(s), if it exists, will be deleted.

[2.3.0] - 2022-02-28
~~~~~~~~~~~~~~~~~~~~
* Add REST API functionality to update verified name status, and to delete verified names.

[2.2.1] - 2022-02-23
~~~~~~~~~~~~~~~~~~~~
* Update verified name status to `denied` if proctoring `error` status is received

[2.2.0] - 2022-02-14
~~~~~~~~~~~~~~~~~~~~
* Added Django40 testing and dropped Django22, 30 and 31 support

[2.1.0] - 2022-01-11
~~~~~~~~~~~~~~~~~~~~
* Add optional `statuses_to_exclude` argument to `get_verified_name` in order to filter out one or
  more statuses from the result.

[2.0.3] - 2021-11-17
~~~~~~~~~~~~~~~~~~~~
* Remove unused celery tasks

[2.0.2] - 2021-11-16
~~~~~~~~~~~~~~~~~~~~
* Cut over to new celery tasks for IDV and proctoring handlers.

[2.0.1] - 2021-11-15
~~~~~~~~~~~~~~~~~~~~
* If we receive a non-relevant status for either IDV or proctoring, do not
  trigger a celery task.

[2.0.0] - 2021-10-27
~~~~~~~~~~~~~~~~~~~~~
* Remove VERIFIED_NAME_FLAG and all references to it.
* Remove VerifiedNameEnabledView view.
* Remove verified_name_enabled key from responses for VerifiedNameView view and VerifiedNameHistoryView

[1.0.3] - 2021-10-26
~~~~~~~~~~~~~~~~~~~~~
* Add system check to CI.
* Add additional logs to IDV signal handler and Celery task logic.

[1.0.2] - 2021-09-29
~~~~~~~~~~~~~~~~~~~~~
* Add automatic retry logic to celery tasks.

[1.0.1] - 2021-09-28
~~~~~~~~~~~~~~~~~~~~~
* Move toggle check out of tasks

[1.0.0] - 2021-09-23
~~~~~~~~~~~~~~~~~~~~~
* Move signal receiver logic into celery task

[0.11.0] - 2021-09-15
~~~~~~~~~~~~~~~~~~~~~
* Add name change validator

[0.10.0] - 2021-09-13
~~~~~~~~~~~~~~~~~~~~~
* Add is verified name enabled endpoint

[0.9.2] - 2021-09-07
~~~~~~~~~~~~~~~~~~~~
* Update IDV signal handler field names to be more explicit about the received names.

[0.9.1] - 2021-09-07
~~~~~~~~~~~~~~~~~~~~
* Add extra validation for the VerifiedName serializer, throwing a 400 error if
  `verified_name` contains HTML or a URL.

[0.9.0] - 2021-09-01
~~~~~~~~~~~~~~~~~~~~
* Add is verified name enabled to the API
* ADR for the use of signals in name affirmation service

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
