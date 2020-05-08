from exchangelib import Credentials, Account

credentials = Credentials('john@example.com', 'topsecret')
account = Account('john@example.com', credentials=credentials, autodiscover=True)

for item in account.inbox.all().order_by('-datetime_received')[:100]:
    print(item.subject, item.sender, item.datetime_received)
 
    
###Folders

#All wellknown folders are available as properties on the account, e.g. as account.root, account.calendar, account.trash, account.inbox, account.outbox, account.sent, account.junk, account.tasks and account.contacts.

# There are multiple ways of navigating the folder tree and searching for folders. Globbing and 
# absolute path may create unexpected results if your folder names contain slashes.

# The folder structure is cached after first access to a folder hierarchy. This means that external
# changes to the folder structure will not show up until you clear the cache. Here's how to clear
# the cache of each of the currently supported folder hierarchies:
from exchangelib import Account, Folder,FolderCollection

a = Account(...)
a.root.refresh()
a.public_folders_root.refresh()
a.archive_root.refresh()

some_folder = a.root / 'Some Folder'
some_folder.parent
some_folder.parent.parent.parent
some_folder.root  # Returns the root of the folder structure, at any level. Same as Account.root
some_folder.children  # A generator of child folders
some_folder.absolute  # Returns the absolute path, as a string
some_folder.walk()  # A generator returning all subfolders at arbitrary depth this level
# Globbing uses the normal UNIX globbing syntax
some_folder.glob('foo*')  # Return child folders matching the pattern
some_folder.glob('*/foo')  # Return subfolders named 'foo' in any child folder
some_folder.glob('**/foo')  # Return subfolders named 'foo' at any depth
some_folder / 'sub_folder' / 'even_deeper' / 'leaf'  # Works like pathlib.Path
# You can also drill down into the folder structure without using the cache. This works like
# the single slash syntax, but does not start by creating a cache the folder hierarchy. This is
# useful if your account contains a huge number of folders, and you already know where to go.
some_folder // 'sub_folder' // 'even_deeper' // 'leaf'
some_folder.parts  # returns some_folder and all its parents, as Folder instances
# tree() returns a string representation of the tree structure at the given level
print(a.root.tree())
'''
root
鈹溾攢鈹� inbox
鈹�   鈹斺攢鈹� todos
鈹斺攢鈹� archive
    鈹溾攢鈹� Last Job
    鈹溾攢鈹� exchangelib issues
    鈹斺攢鈹� Mom
'''

# Folders have some useful counters:
a.inbox.total_count
a.inbox.child_folder_count
a.inbox.unread_count
# Update the counters
a.inbox.refresh()

# Folders can be created, updated and deleted:
f = Folder(parent=a.inbox, name='My New Folder')
f.save()

f.name = 'My New Subfolder'
f.save()
f.delete()

# Delete all items in a folder
f.empty()
# Also delete all subfolders in the folder
f.empty(delete_sub_folders=True)
# Recursively delete all items in a folder, and all subfolders and their content. This is
# like `empty(delete_sub_folders=True)` but attempts to protect distinguished folders from
# being deleted. Use with caution!
f.wipe()



###Dates, datetimes and timezones

from datetime import datetime, timedelta
import pytz
from exchangelib import EWSTimeZone, EWSDateTime, EWSDate

# EWSTimeZone works just like pytz.timezone()
tz = EWSTimeZone.timezone('Europe/Copenhagen')
# You can also get the local timezone defined in your operating system
tz = EWSTimeZone.localzone()

# EWSDate and EWSDateTime work just like datetime.datetime and datetime.date. Always create
# timezone-aware datetimes with EWSTimeZone.localize():
localized_dt = tz.localize(EWSDateTime(2017, 9, 5, 8, 30))
right_now = tz.localize(EWSDateTime.now())

# Datetime math works transparently
two_hours_later = localized_dt + timedelta(hours=2)
two_hours = two_hours_later - localized_dt
two_hours_later += timedelta(hours=2)

# Dates
my_date = EWSDate(2017, 9, 5)
today = EWSDate.today()
also_today = right_now.date()
also_today += timedelta(days=10)

# UTC helpers. 'UTC' is the UTC timezone as an EWSTimeZone instance.
# 'UTC_NOW' returns a timezone-aware UTC timestamp of current time.
from exchangelib import UTC, UTC_NOW

right_now_in_utc = UTC.localize(EWSDateTime.now())
right_now_in_utc = UTC_NOW()

# Already have a Python datetime object you want to use? Make sure it's localized. Then pass 
# it to from_datetime().
pytz_tz = pytz.timezone('Europe/Copenhagen')
py_dt = pytz_tz.localize(datetime(2017, 12, 11, 10, 9, 8))
ews_now = EWSDateTime.from_datetime(py_dt)



###Creating, updating, deleting, sending, moving, archiving

# Here's an example of creating a calendar item in the user's standard calendar.  If you want to
# access a non-standard calendar, choose a different one from account.folders[Calendar].
#
# You can create, update and delete single items:
from exchangelib import Account, CalendarItem, Message, Mailbox, FileAttachment, HTMLBody
from exchangelib.items import SEND_ONLY_TO_ALL, SEND_ONLY_TO_CHANGED
from exchangelib.properties import DistinguishedFolderId

a = Account(...)
item = CalendarItem(folder=a.calendar, subject='foo')
item.save()  # This gives the item an 'id' and a 'changekey' value
item.save(send_meeting_invitations=SEND_ONLY_TO_ALL)  # Send a meeting invitation to attendees
# Update a field. All fields have a corresponding Python type that must be used.
item.subject = 'bar'
# Print all available fields on the 'CalendarItem' class. Beware that some fields are read-only, or
# read-only after the item has been saved or sent, and some fields are not supported on old
# versions of Exchange.
print(CalendarItem.FIELDS)
item.save()  # When the items has an item_id, this will update the item
item.save(update_fields=['subject'])  # Only updates certain fields. Accepts a list of field names.
item.save(send_meeting_invitations=SEND_ONLY_TO_CHANGED)  # Send invites only to attendee changes
item.delete()  # Hard deletinon
item.delete(send_meeting_cancellations=SEND_ONLY_TO_ALL)  # Send cancellations to all attendees
item.soft_delete()  # Delete, but keep a copy in the recoverable items folder
item.move_to_trash()  # Move to the trash folder
item.move(a.trash)  # Also moves the item to the trash folder
item.copy(a.trash)  # Creates a copy of the item to the trash folder
item.archive(DistinguishedFolderId('inbox'))  # Archives the item to inbox of the the archive mailbox

# You can also send emails. If you don't want a local copy:
m = Message(
    account=a,
    subject='Daily motivation',
    body='All bodies are beautiful',
    to_recipients=[
        Mailbox(email_address='anne@example.com'),
        Mailbox(email_address='bob@example.com'),
    ],
    cc_recipients=['carl@example.com', 'denice@example.com'],  # Simple strings work, too
    bcc_recipients=[
        Mailbox(email_address='erik@example.com'),
        'felicity@example.com',
    ],  # Or a mix of both
)
m.send()

# Or, if you want a copy in e.g. the 'Sent' folder
m = Message(
    account=a,
    folder=a.sent,
    subject='Daily motivation',
    body='All bodies are beautiful',
    to_recipients=[Mailbox(email_address='anne@example.com')]
)
m.send_and_save()

# Likewise, you can reply to and forward messages that are stored in your mailbox (i.e. they
# have an item ID).
m = a.sent.get(subject='Daily motivation')
m.reply(
    subject='Re: Daily motivation',
    body='I agree',
    to_recipients=['carl@example.com', 'denice@example.com']
)
m.reply_all(subject='Re: Daily motivation', body='I agree')
m.forward(
    subject='Fwd: Daily motivation',
    body='Hey, look at this!', 
    to_recipients=['carl@example.com', 'denice@example.com']
)

# You can also edit a draft of a reply or forward
forward_draft = m.create_forward(
    subject='Fwd: Daily motivation',
    body='Hey, look at this!',
    to_recipients=['carl@example.com', 'denice@example.com']
).save(a.drafts) # gives you back the item
forward_draft.reply_to = ['erik@example.com']
forward_draft.attach(FileAttachment(name='my_file.txt', content='hello world'.encode('utf-8')))
forward_draft.send() # now our forward has an extra reply_to field and an extra attachment.

# EWS distinguishes between plain text and HTML body contents. If you want to send HTML body
# content, use the HTMLBody helper. Clients will see this as HTML and display the body correctly:
item.body = HTMLBody('<html><body>Hello happy <blink>OWA user!</blink></body></html>')







#Bulk operations

# Build a list of calendar items
from exchangelib import Account, CalendarItem, EWSDateTime, EWSTimeZone, Attendee, Mailbox
from exchangelib.properties import DistinguishedFolderId

a = Account(...)
tz = EWSTimeZone.timezone('Europe/Copenhagen')
year, month, day = 2016, 3, 20
calendar_items = []
for hour in range(7, 17):
    calendar_items.append(CalendarItem(
        start=tz.localize(EWSDateTime(year, month, day, hour, 30)),
        end=tz.localize(EWSDateTime(year, month, day, hour + 1, 15)),
        subject='Test item',
        body='Hello from Python',
        location='devnull',
        categories=['foo', 'bar'],
        required_attendees = [Attendee(
            mailbox=Mailbox(email_address='user1@example.com'),
            response_type='Accept'
        )]
    ))

# Create all items at once
return_ids = a.bulk_create(folder=a.calendar, items=calendar_items)

# Bulk fetch, when you have a list of item IDs and want the full objects. Returns a generator.
calendar_ids = [(i.id, i.changekey) for i in calendar_items]
items_iter = a.fetch(ids=calendar_ids)
# If you only want some fields, use the 'only_fields' attribute
items_iter = a.fetch(ids=calendar_ids, only_fields=['start', 'subject'])

# Bulk update items. Each item must be accompanied by a list of attributes to update
updated_ids = a.bulk_update(items=[(i, ('start', 'subject')) for i in calendar_items])

# Move many items to a new folder
new_ids = a.bulk_move(ids=calendar_ids, to_folder=a.other_calendar)

# Send draft messages in bulk
message_ids = a.drafts.all().only('id', 'changekey')
new_ids = a.bulk_send(ids=message_ids, save_copy=False)

# Delete in bulk
delete_results = a.bulk_delete(ids=calendar_ids)

# Archive in bulk
delete_results = a.bulk_archive(ids=calendar_ids, to_folder=DistinguishedFolderId('inbox'))

# Bulk delete items found as a queryset
a.inbox.filter(subject__startswith='Invoice').delete()

# Likewise, you can bulk send, copy, move or archive items found in a QuerySet
a.drafts.filter(subject__startswith='Invoice').send()
# All kwargs are passed on to the equivalent bulk methods on the Account
a.drafts.filter(subject__startswith='Invoice').send(save_copy=False)
a.inbox.filter(subject__startswith='Invoice').copy(to_folder=a.inbox / 'Archive')
a.inbox.filter(subject__startswith='Invoice').move(to_folder=a.inbox / 'Archive')
a.inbox.filter(subject__startswith='Invoice').archive(to_folder=DistinguishedFolderId('inbox'))

# You can change the default page size of bulk operations if you have a slow or busy server
a.inbox.filter(subject__startswith='Invoice').delete(page_size=25)




#Searching

from datetime import timedelta
from exchangelib import Account, EWSDateTime, FolderCollection, Q, Message

a = Account(...)

# Not all fields on an item support searching. Here's the list of options for Message items
print([f.name for f in Message.FIELDS if f.is_searchable])

all_items = a.inbox.all()  # Get everything
all_items_without_caching = a.inbox.all().iterator()  # Get everything, but don't cache
# Chain multiple modifiers to refine the query
filtered_items = a.inbox.filter(subject__contains='foo').exclude(categories__icontains='bar')
status_report = a.inbox.all().delete()  # Delete the items returned by the QuerySet
start = a.default_timezone.localize(EWSDateTime(2017, 1, 1))
end = a.default_timezone.localize(EWSDateTime(2018, 1, 1))
items_for_2017 = a.calendar.filter(start__range=(start, end))  # Filter by a date range

# Same as filter() but throws an error if exactly one item isn't returned
item = a.inbox.get(subject='unique_string')

# If you only have the ID and possibly the changekey of an item, you can get the full item:
a.inbox.get(id='AAMkADQy=')
a.inbox.get(id='AAMkADQy=', changekey='FwAAABYA')

# You can sort by a single or multiple fields. Prefix a field with '-' to reverse the sorting. 
# Sorting is efficient since it is done server-side, except when a calendar view sorting on 
# multiple fields.
ordered_items = a.inbox.all().order_by('subject')
reverse_ordered_items = a.inbox.all().order_by('-subject')
 # Indexed properties can be ordered on their individual components
sorted_by_home_street = a.contacts.all().order_by('physical_addresses__Home__street')
# Beware that sorting is done client-side here
a.calendar.view(start=start, end=end).order_by('subject', 'categories')

# Counting and exists
n = a.inbox.all().count()  # Efficient counting
folder_is_empty = not a.inbox.all().exists()  # Efficient tasting

# Restricting returned attributes
sparse_items = a.inbox.all().only('subject', 'start')
# Dig deeper on indexed properties
sparse_items = a.contacts.all().only('phone_numbers')
sparse_items = a.contacts.all().only('phone_numbers__CarPhone')
sparse_items = a.contacts.all().only('physical_addresses__Home__street')

# Return values as dicts, not objects
ids_as_dict = a.inbox.all().values('id', 'changekey')
# Return values as nested lists
values_as_list = a.inbox.all().values_list('subject', 'body')
# Return values as a flat list
all_subjects = a.inbox.all().values_list('physical_addresses__Home__street', flat=True)

# A QuerySet can be indexed and sliced like a normal Python list. Slicing and indexing of the
# QuerySet is efficient because it only fetches the necessary items to perform the slicing.
# Slicing from the end is also efficient, but then you might as well reverse the sorting.
first_ten = a.inbox.all().order_by('-subject')[:10]  # Efficient. We only fetch 10 items
last_ten = a.inbox.all().order_by('-subject')[:-10]  # Efficient, but convoluted
next_ten = a.inbox.all().order_by('-subject')[10:20]  # Efficient. We only fetch 10 items
single_item = a.inbox.all().order_by('-subject')[34298]  # Efficient. We only fetch 1 item
ten_items = a.inbox.all().order_by('-subject')[3420:3430]  # Efficient. We only fetch 10 items
random_emails = a.inbox.all().order_by('-subject')[::3]  # This is just stupid, but works

# The syntax for filter() is modeled after Django QuerySet filters. The following filter lookup 
# types are supported. Some lookups only work with string attributes. Range and less/greater 
# operators only work for date or numerical attributes. Some attributes are not searchable at all 
# via EWS:
qs = a.calendar.all()
qs.filter(subject='foo')  # Returns items where subject is exactly 'foo'. Case-sensitive
qs.filter(start__range=(start, end))  # Returns items within range
qs.filter(subject__in=('foo', 'bar'))  # Return items where subject is either 'foo' or 'bar'
qs.filter(subject__not='foo')  # Returns items where subject is not 'foo'
qs.filter(start__gt=start)  # Returns items starting after 'dt'
qs.filter(start__gte=start)  # Returns items starting on or after 'dt'
qs.filter(start__lt=start)  # Returns items starting before 'dt'
qs.filter(start__lte=start)  # Returns items starting on or before 'dt'
qs.filter(subject__exact='foo')  # Same as filter(subject='foo')
qs.filter(subject__iexact='foo')  #  Returns items where subject is 'foo', 'FOO' or 'Foo'
qs.filter(subject__contains='foo')  # Returns items where subject contains 'foo'
qs.filter(subject__icontains='foo')  # Returns items where subject contains 'foo', 'FOO' or 'Foo'
qs.filter(subject__startswith='foo')  # Returns items where subject starts with 'foo'
# Returns items where subject starts with 'foo', 'FOO' or 'Foo'
qs.filter(subject__istartswith='foo')
# Returns items that have at least one category assigned, i.e. the field exists on the item on the 
# server.
qs.filter(categories__exists=True)
# Returns items that have no categories set, i.e. the field does not exist on the item on the 
# server.
qs.filter(categories__exists=False)

# WARNING: Filtering on the 'body' field is not fully supported by EWS. There seems to be a window
# before some internal search index is populated where case-sensitive or case-insensitive filtering
# for substrings in the body element incorrectly returns an empty result, and sometimes the result
# stays empty.

# filter() also supports EWS QueryStrings. Just pass the string to filter(). QueryStrings cannot
# be combined with other filters. We make no attempt at validating the syntax of the QueryString 
# - we just pass the string verbatim to EWS.
#
# Read more about the QueryString syntax here:
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/querystring-querystringtype
a.inbox.filter('subject:XXX')

# filter() also supports Q objects that are modeled after Django Q objects, for building complex
# boolean logic search expressions.
q = (Q(subject__iexact='foo') | Q(subject__contains='bar')) & ~Q(subject__startswith='baz')
a.inbox.filter(q)

# In this example, we filter by categories so we only get the items created by us.
a.calendar.filter(
    start__lt=a.default_timezone.localize(EWSDateTime(2019, 1, 1)),
    end__gt=a.default_timezone.localize(EWSDateTime(2019, 1, 31)),
    categories__contains=['foo', 'bar'],
)

# By default, EWS returns only the master recurring item. If you want recurring calendar
# items to be expanded, use calendar.view(start=..., end=...) instead.
items = a.calendar.view(
    start=a.default_timezone.localize(EWSDateTime(2019, 1, 31)),
    end=a.default_timezone.localize(EWSDateTime(2019, 1, 31)) + timedelta(days=1),
)
for item in items:
    print(item.start, item.end, item.subject, item.body, item.location)

# You can combine view() with other modifiers. For example, to check for conflicts before 
# adding a meeting from 8:00 to 10:00:
has_conflicts = a.calendar.view(
    start=a.default_timezone.localize(EWSDateTime(2019, 1, 31, 8)),
    end=a.default_timezone.localize(EWSDateTime(2019, 1, 31, 10)),
    max_items=1
).exists()

# The filtering syntax also works on collections of folders, so you can search multiple folders in 
# a single request.
a.inbox.children.filter(subject='foo')
a.inbox.walk().filter(subject='foo')
a.inbox.glob('foo*').filter(subject='foo')
# Or select the folders individually
FolderCollection(account=a, folders=[a.inbox, a.calendar]).filter(subject='foo')









#Attachments

# It's possible to create, delete and get attachments connected to any item type:
# Process attachments on existing items. FileAttachments have a 'content' attribute
# containing the binary content of the file, and ItemAttachments have an 'item' attribute
# containing the item. The item can be a Message, CalendarItem, Task etc.
import os.path
from exchangelib import Account, FileAttachment, ItemAttachment, Message, CalendarItem, HTMLBody

a = Account
for item in a.inbox.all():
    for attachment in item.attachments:
        if isinstance(attachment, FileAttachment):
            local_path = os.path.join('/tmp', attachment.name)
            with open(local_path, 'wb') as f:
                f.write(attachment.content)
            print('Saved attachment to', local_path)
        elif isinstance(attachment, ItemAttachment):
            if isinstance(attachment.item, Message):
                print(attachment.item.subject, attachment.item.body)

# Streaming downloads of file attachment is supported. This reduces memory consumption since we
# never store the full content of the file in-memory:
for item in a.inbox.all():
    for attachment in item.attachments:
        if isinstance(attachment, FileAttachment):
            local_path = os.path.join('/tmp', attachment.name)
            with open(local_path, 'wb') as f, attachment.fp as fp:
                buffer = fp.read(1024)
                while buffer:
                    f.write(buffer)
                    buffer = fp.read(1024)
            print('Saved attachment to', local_path)

# Create a new item with an attachment
item = Message(...)
binary_file_content = 'Hello from unicode 忙酶氓'.encode('utf-8')  # Or read from file, BytesIO etc.
my_file = FileAttachment(name='my_file.txt', content=binary_file_content)
item.attach(my_file)
my_calendar_item = CalendarItem(...)
my_appointment = ItemAttachment(name='my_appointment', item=my_calendar_item)
item.attach(my_appointment)
item.save()

# Add an attachment on an existing item
my_other_file = FileAttachment(name='my_other_file.txt', content=binary_file_content)
item.attach(my_other_file)

# Remove the attachment again
item.detach(my_file)

# If you want to embed an image in the item body, you can link to the file in the HTML
message = Message(...)
logo_filename = 'logo.png'
with open(logo_filename, 'rb') as f:
    my_logo = FileAttachment(name=logo_filename, content=f.read(), is_inline=True, content_id=logo_filename)
message.attach(my_logo)
message.body = HTMLBody('<html><body>Hello logo: <img src="cid:%s"></body></html>' % logo_filename)

# Attachments cannot be updated via EWS. In this case, you must to detach the attachment, update
# the relevant fields, and attach the updated attachment.

# Be aware that adding and deleting attachments from items that are already created in Exchange
# (items that have an item_id) will update the changekey of the item.