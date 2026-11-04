# Nextcloud

## What is it?

Nextcloud is a free, open-source file-sharing and collaboration platform that organizations host on their own servers. It gives companies full control over their files and data — unlike Dropbox or Google Drive, the data never leaves the organization's infrastructure.

## What does it do?

- File upload, download, and organization in folders
- File sharing between users and groups with configurable permissions
- Collaborative document editing (with OnlyOffice or Collabora integration)
- User and group management with role-based access control
- Activity logging and audit trails
- Mobile and desktop sync clients
- [REST](../../../concepts/backend/api/rest.md) and [WebDAV](../../../concepts/protocols/webdav.md) APIs for programmatic file access

## How it fits in this project

Nextcloud is the **core platform** of this project. It is not rebuilt — it is deployed as-is and used as the document management backbone. All user-facing file operations (upload, share, organize, access) happen through Nextcloud. The AI/[RAG](../../../concepts/ai/rag/rag.md) layer connects to Nextcloud via its [WebDAV](../../../concepts/protocols/webdav.md)/API to read and index documents.

## Deployment

Nextcloud is deployed as a [Docker](../../../concepts/containers/docker.md) container using the official `nextcloud` [Docker](../../../concepts/containers/docker.md) image, orchestrated by [Docker Compose](../../../concepts/containers/docker-compose.md), running on an Ubuntu VM on [Microsoft Azure](../../../concepts/cloud/azure/azure.md).

## Key Concepts

| Term | Meaning |
|---|---|
| Admin | Superuser who manages users, groups, and system settings |
| Group | A collection of users who share the same access permissions |
| Share | Making a file or folder accessible to another user, group, or link |
| [WebDAV](../../../concepts/protocols/webdav.md) | A protocol that allows external apps to access Nextcloud files as a file system |
| OCS API | Nextcloud's [REST](../../../concepts/backend/api/rest.md) API for user management and app integration |
| Activity App | Built-in app that logs file access, uploads, shares, and deletions |
| Admin Audit Log | App that logs administrative actions for compliance and security review |

## Official Resources

| Resource | Link |
|---|---|
| Website | https://nextcloud.com |
| GitHub Repository | https://github.com/nextcloud/server |
| [Docker](../../../concepts/containers/docker.md) Hub Image | https://hub.docker.com/_/nextcloud |
| Official Documentation | https://docs.nextcloud.com |
| Admin Manual | https://docs.nextcloud.com/server/latest/admin_manual |
| User Manual | https://docs.nextcloud.com/server/latest/user_manual |
| [WebDAV](../../../concepts/protocols/webdav.md) API Reference | https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html |
| OCS API Reference | https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/index.html |
| [Docker](../../../concepts/containers/docker.md) Image Docs (README) | https://github.com/nextcloud/docker |
| Releases / Changelog | https://nextcloud.com/changelog |

## Related

- [WebDAV API](webdav-api.md)
- [Access Control & IAM](../../../concepts/security/authorization/access-control-iam.md)
- [Ubuntu Server Setup](../../linux/ubuntu-server-setup.md)
- [Docker](../../../concepts/containers/docker.md)
- [Docker Compose](../../../concepts/containers/docker-compose.md)
