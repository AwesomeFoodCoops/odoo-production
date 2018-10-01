Memberspace Area for Foodcoop
=============================
## Email Alias feature

# Concept
- Each team/template will have 2 email alias:
  - 1 for the Coordinators of the team, naming convention of alias for Coordinators: coordos.[week][day][hour]@[domain]
  - 1 for the Members of the Team (including the Coordinators): naming convention of alias for Members: service.[week][day][hour]@[domain]

- Alias domain is configured by parameter object:
  * with key: mail.catchall.domain.
  * value: your email domain (e.g: cooplaloue.fr)
  When installing module, there is a script to create email alias automatically for each template, so, mail.catchall.domain must exist
before installing coop_memberspace module.

- There are 2 main objects to store email alias for each team:
  - memberspace_alias: store all alias of team (access via Member config menu: Members > Configuration > Memberspace Alias)
  - memberspace_conversation: store all conversation of each topic (access via Member config menu: Members > Configuration > Memberspace Conversation). Every time a new email which sent to specific alias, a new conversation will be created, then after that, all reply of the
  conversation will be stored within this conversation.

# How Alias works?

Any mail sent to your domain, that doesn't have a defined mailbox, will be sent to your catchall email. Application fetches the emails with a cron (using the module fetchmail) and dispatches them to corresponding virtual mail address (alias)

Note: Make sure you set your created mailbox of Incoming Mail Server as the catch-all.