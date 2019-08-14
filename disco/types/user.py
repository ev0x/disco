from holster.enum import Enum

from datetime import datetime
from disco.types.base import (
    SlottedModel, Field, snowflake, text, with_equality, with_hash, ListField,
    cached_property
)

DefaultAvatars = Enum(
    BLURPLE=0,
    GREY=1,
    GREEN=2,
    ORANGE=3,
    RED=4,
)


class User(SlottedModel, with_equality('id'), with_hash('id')):
    id = Field(snowflake)
    username = Field(text)
    avatar = Field(text)
    discriminator = Field(text)
    bot = Field(bool, default=False)
    verified = Field(bool)
    email = Field(text)

    presence = Field(None)

    def get_avatar_url(self, still_format='webp', animated_format='gif', size=1024):
        if not self.avatar:
            return 'https://cdn.discordapp.com/embed/avatars/{}.png'.format(self.default_avatar)

        if self.avatar.startswith('a_'):
            return 'https://cdn.discordapp.com/avatars/{}/{}.{}?size={}'.format(
                self.id, self.avatar, animated_format, size
            )
        else:
            return 'https://cdn.discordapp.com/avatars/{}/{}.{}?size={}'.format(
                self.id, self.avatar, still_format, size
            )

    @property
    def default_avatar(self):
        return DefaultAvatars[int(self.discriminator) % len(DefaultAvatars.attrs)]

    @property
    def avatar_url(self):
        return self.get_avatar_url()

    @property
    def mention(self):
        return '<@{}>'.format(self.id)

    def open_dm(self):
        return self.client.api.users_me_dms_create(self.id)

    def __str__(self):
        return u'{}#{}'.format(self.username, str(self.discriminator).zfill(4))

    def __repr__(self):
        return u'<User {} ({})>'.format(self.id, self)


GameType = Enum(
    DEFAULT=0,
    STREAMING=1,
    LISTENING=2,
    WATCHING=3,
    CUSTOM_STATUS=4,
)

Status = Enum(
    'ONLINE',
    'IDLE',
    'DND',
    'INVISIBLE',
    'OFFLINE',
)

ClientPresenceStatus = Enum(
    'ONLINE',
    'IDLE',
    'DND',
    'OFFLINE',
)

class Party(SlottedModel):
    id = Field(text)
    size = ListField(int)


class Assets(SlottedModel):
    large_image = Field(text)
    large_text = Field(text)
    small_image = Field(text)
    small_text = Field(text)


class Secrets(SlottedModel):
    join = Field(text)
    spectate = Field(text)
    match = Field(text)


class Timestamps(SlottedModel):
    start = Field(int)
    end = Field(int)

    @cached_property
    def start_time(self):
        return datetime.utcfromtimestamp(self.start / 1000)

    @cached_property
    def end_time(self):
        return datetime.utcfromtimestamp(self.end / 1000)


class Game(SlottedModel):
    type = Field(GameType)
    name = Field(text)
    url = Field(text)
    timestamps = Field(Timestamps)
    application_id = Field(text)
    details = Field(text)
    state = Field(text)
    party = Field(Party)
    assets = Field(Assets)
    secrets = Field(Secrets)
    instance = Field(bool)
    flags = Field(int)

class ClientStatus(SlottedModel):
    desktop = Field(ClientPresenceStatus)
    mobile = Field(ClientPresenceStatus)
    web = Field(ClientPresenceStatus)


class Presence(SlottedModel):
    user = Field(User, alias='user', ignore_dump=['presence'])
    game = Field(Game)
    status = Field(Status)
    activities = ListField(Game)
    client_status = Field(ClientStatus)
