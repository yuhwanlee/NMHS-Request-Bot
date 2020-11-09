import discord
from discord import Embed
import random
import uuid
import string
import csv
from AWS import AWSFileManager

client = discord.Client()


def parse_id(author):
    raw = author.mention
    if raw.find('!') != -1:
        return raw[3:-1]
    return raw[2:-1]


def write_new_request(embed):
    # getting the string values of each embed proxy, and then removing the commas.
    data = [proxy.value.replace(',', '') for proxy in embed.fields]
    name, grade, date, time, subject, username, *other = data
    aws_file_manager.download_unaccepted()

    request_id = random_uuid(6)
    with open("unaccepted_requests.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        if len(other) > 0:
            writer.writerow([request_id, name, grade, date, time, subject, username, other[0]])
        else:
            writer.writerow([request_id, name, grade, date, time, subject, username, ""])

    aws_file_manager.upload_unaccepted()

    embed = Embed(title="NEW REQUEST **{}**".format(request_id))
    embed.add_field(name="Student name:", value=name, inline=False)
    embed.add_field(name="Grade:", value=grade, inline=False)
    embed.add_field(name="Day:", value=date, inline=False)
    embed.add_field(name="Time:", value=time, inline=False)
    embed.add_field(name="Subject:", value=subject, inline=False)
    embed.add_field(name="Discord username:", value=username, inline=False)
    if len(other) > 0 and len(other[0]) > 0:
        embed.add_field(name="Other comments:", value=other[0], inline=False)
    return embed



def accept_request(request_id, user_id, nickname):
    found = False
    found_row = []
    write_rows = []
    tutee_name = ''
    day = ''
    time = ''

    aws_file_manager.download_unaccepted()
    with open('unaccepted_requests.csv', 'r') as src:
        reader = csv.reader(src)
        # see if the requestid exists in the unaccepted requests. if it is, save the data
        for row in reader:
            if row[0] == str(request_id):
                found = True
                found_row = row
                tutee_name = row[1]
                day = row[3]
                time = row[4]
            else:
                write_rows.append(row)
    # print(write_rows)
    with open('unaccepted_requests.csv', 'w', newline='') as dest:
        writer = csv.writer(dest)
        for row in write_rows:
            writer.writerow(row)
    aws_file_manager.upload_unaccepted()
    # transfer the data to the accepted requests if the request id is found.
    if found:
        aws_file_manager.download_accepted()

        with open('accepted_requests.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            found_row.insert(1, user_id)  # inserting user id to 2nd index
            found_row.insert(2, nickname)
            writer.writerow(found_row)
        aws_file_manager.upload_accepted()

        return True, tutee_name, day, time
    else:
        return False, '', '', ''


def get_accepted_requests(user_id, nickname):
    embeds = []
    requests = []
    aws_file_manager.download_accepted()
    # go through all the accepted requests (for the user) and store them
    with open('accepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == str(user_id):
                requests.append(row)

    # if there are accepted requests for that user, then return an embed with the information.
    if len(requests) > 0:
        embed = Embed(title='Accepted requests for **{}**:'.format(nickname))
        for request in requests:
            request_id, user_id, user_nick, name, grade, day, time, subject, username, *other = request
            embed.add_field(name='Request **{}**:'.format(request_id), value='{}, {} - {}'.format(subject, day, time),
                            inline=False)
        embeds.append(embed)
    else:
        embed = Embed(title='Accepted requests for **{}**:'.format(nickname))
        embed.add_field(name='No accepted requests.', value='Accept requests with the !accept command')
        embeds.append(embed)
    return embeds


def undo_request(request_id):
    found = False
    found_row = []
    write_rows = []
    tutee_name = []
    day = []
    time = []
    aws_file_manager.download_accepted()
    # see if the request is an accepted request.
    with open('accepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(request_id):
                found = True
                found_row = row
                tutee_name = row[3]
                day = row[5]
                time = row[6]
            else:
                write_rows.append(row)
    with open('accepted_requests.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in write_rows:
            writer.writerow(row)
    aws_file_manager.upload_accepted()
    # if it is an accepted request, then move it to unaccepted requests.
    if found:
        aws_file_manager.download_unaccepted()
        with open('unaccepted_requests.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            found_row.pop(1)  # inserting user id to 2nd index
            found_row.pop(1)
            writer.writerow(found_row)
        aws_file_manager.upload_unaccepted()
        return True, tutee_name, day, time
    else:
        return False, '', '', ''


def remove_request(request_id):
    unaccepted = False
    accepted = False
    found = False
    write_rows = []
    aws_file_manager.download_unaccepted()
    aws_file_manager.download_accepted()
    with open('unaccepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(request_id):
                found = True
                unaccepted = True
            else:
                write_rows.append(row)
    if not found:
        write_rows = []
        with open('accepted_requests.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(request_id):
                    found = True
                    accepted = True
                else:
                    write_rows.append(row)
    if found:
        if unaccepted:
            with open('unaccepted_requests.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in write_rows:
                    writer.writerow(row)
            aws_file_manager.upload_unaccepted()
        if accepted:
            with open('accepted_requests.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in write_rows:
                    writer.writerow(row)
            aws_file_manager.upload_accepted()
        return True
    else:
        return False


def list_requests():
    embeds = []
    unaccepted_rows = []
    accepted_rows = []
    aws_file_manager.download_unaccepted()
    aws_file_manager.download_accepted()
    with open('unaccepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip first row i think
        for row in reader:
            unaccepted_rows.append(row)

    with open('accepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            accepted_rows.append(row)
    if len(unaccepted_rows) > 0:
        embed = Embed(title='**Unaccepted** requests')
        for row in unaccepted_rows:
            request_id, name, grade, day, time, subject, username, *other = row
            embed.add_field(name='Request **{}**:'.format(request_id), value='{}, {} - {}'.format(subject, day, time),
                            inline=False)

        embeds.append(embed)
    if len(accepted_rows) > 0:
        embed = Embed(title='**Accepted** requests')
        for row in accepted_rows:
            request_id, accepted_id, nickname, name, grade, day, time, subject, username, *other = row
            embed.add_field(name='Request **{}** (accepted by {}):'.format(request_id, nickname),
                            value='{}, {} - {}'.format(subject, day, time), inline=False)
        embeds.append(embed)
    if len(accepted_rows) == len(unaccepted_rows) == 0:
        embed = Embed(title='No requests', description='There are no unavailable or available requests.')
        embeds.append(embed)
    return embeds


def request_in_unaccepted(request_id):
    aws_file_manager.download_unaccepted()
    inside = False
    with open('unaccepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(request_id):
                inside = True
    return inside


def request_in_accepted(request_id):
    aws_file_manager.download_accepted()
    inside = False
    with open('accepted_requests.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(request_id):
                inside = True
    return inside


def get_info(request_id):
    aws_file_manager.download_accepted()
    aws_file_manager.download_unaccepted()
    if request_in_unaccepted(request_id):
        found_row = []
        with open('unaccepted_requests.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(request_id):
                    found_row = row

        request_id, name, grade, day, time, subject, username, *other = found_row
        embed = Embed(title='Request **{}**'.format(request_id))
        embed.add_field(name="Student name:", value=name, inline=False)
        embed.add_field(name="Grade:", value=grade, inline=False)
        embed.add_field(name="Day:", value=day, inline=False)
        embed.add_field(name="Time:", value=time, inline=False)
        embed.add_field(name="Subject:", value=subject, inline=False)
        embed.add_field(name="Discord username:", value=username, inline=False)
        if len(other) > 0 and len(other[0]) > 0:
            embed.add_field(name="Other comments:", value=other[0], inline=False)
        return embed
    elif request_in_accepted(request_id):
        found_row = []
        with open('accepted_requests.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(request_id):
                    found_row = row

        request_id, accepted_id, nickname, name, grade, day, time, subject, username, *other = found_row
        embed = Embed(title='Request **{}**'.format(request_id))
        embed.add_field(name="Tutor that accepted:", value=nickname, inline=False)
        embed.add_field(name="Student name:", value=name, inline=False)
        embed.add_field(name="Grade:", value=grade, inline=False)
        embed.add_field(name="Day:", value=day, inline=False)
        embed.add_field(name="Time:", value=time, inline=False)
        embed.add_field(name="Subject:", value=subject, inline=False)
        embed.add_field(name="Discord username:", value=username, inline=False)
        if len(other) > 0 and len(other[0]) > 0:
            embed.add_field(name="Other comments:", value=other[0], inline=False)
        return embed
    else:
        return Embed(title='Request **{}** not found.'.format(request_id))


def manually_write_request(data):
    aws_file_manager.download_unaccepted()
    data.insert(0, random_uuid(6))
    with open('unaccepted_requests.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    aws_file_manager.upload_unaccepted()


def random_uuid(length):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=length))


def truncated_uuid(length):
    return str(uuid.uuid4())[:length]


aws_file_manager = AWSFileManager()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    nickname = message.author.display_name.replace(',', '')

    webhook_channel = 767181694817009685
    tutoring_notification_channel = 766006315432411176
    command_channel = 768561476868374588
    announcement_channel = 766121926279168061

    roles = []
    role_names = []
    is_admin = False
    is_board = False
    is_bot_master = False
    if message.channel.id != webhook_channel:
        roles = message.author.roles
        role_names = [role.name.lower() for role in roles]
        is_admin = 'admin' in role_names
        is_board = 'board' in role_names
        is_bot_master = 'bot master' in role_names


    user_id = parse_id(message.author)
    message_list = message.content.split(' ')
    if message.channel.id == webhook_channel:  # if in webhook channel
        if len(message.embeds) > 0:  # if message is an embed
            embed = write_new_request(message.embeds[0])
            channel = client.get_channel(tutoring_notification_channel)
            await channel.send(embed=embed)

    elif message.channel.id == command_channel:  # if in command channel
        if len(message_list) > 1:
            if message_list[1] == 'request_id':
                return

        if message.content.startswith("!accept"):
            if len(message_list) > 1:
                request_id = message_list[1]
                if request_id.lower() == 'request_id':
                    return
                accepted, tutee_name, day, time = accept_request(request_id=request_id, user_id=user_id, nickname=nickname)
                if accepted:
                    await message.channel.send('Request **{}** accepted!'.format(request_id))
                    channel = client.get_channel(announcement_channel)
                    mentionable_name = message.author.mention
                    await channel.send('**{}**\'s request was accepted by {} (**{}** @ **{}**, Request ID: **{}**)!'.format(tutee_name, mentionable_name, day, time, request_id))
                else:
                    await message.channel.send('Invalid request ID.')
            else:
                embed = Embed(title='!accept', description='Allows you to accept a tutoring request')
                embed.add_field(name="Usage:", value="!accept [request ID]")
                await message.channel.send(embed=embed)

        if message.content.startswith("!info"):
            if len(message_list) > 1:
                request_id = message_list[1]
                embed = get_info(request_id)
                await message.channel.send(embed=embed)
            else:
                embed = Embed(title='!info', description='Gives you information about a tutoring request')
                embed.add_field(name="Usage:", value="!info [request ID]")
                await message.channel.send(embed=embed)

        if message.content.startswith("!myrequests"):
            embeds = get_accepted_requests(user_id=user_id, nickname=nickname)
            for embed in embeds:
                await message.channel.send(embed=embed)

        if message.content.startswith("!list"):
            embeds = list_requests()
            for embed in embeds:
                await message.channel.send(embed=embed)

        if message.content.startswith("!unaccept"):
            if is_board or is_bot_master:
                if len(message_list) > 1:
                    request_id = message_list[1]
                    found, tutee_name, day, time = undo_request(request_id=request_id, user_id=user_id)
                    if found:
                        await message.channel.send('Request **{}** unaccepted!'.format(request_id))
                        channel = client.get_channel(announcement_channel)
                        await channel.send('**{}**\'s request (Request ID: **{}**) was unaccepted! (**{}** @ **{}**)'.format(tutee_name, request_id, day, time))
                    else:
                        await message.channel.send('Invalid request ID.')
                else:
                    embed = Embed(title='!unaccept', description='Allows you to unaccept a tutoring request')
                    embed.add_field(name="Usage:", value="!unaccept [request_ID]")
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send('You do not have permission to use this command.')

        if message.content.startswith("!remove"):
            if is_board or is_bot_master:
                if len(message_list) > 1:
                    request_id = message_list[1]
                    if remove_request(request_id=request_id):
                        await message.channel.send('Request **{}** removed!'.format(request_id))
                    else:
                        await message.channel.send("Invalid request ID.")
                else:
                    embed = Embed(title='!remove', description='Allows you to remove a tutoring request')
                    embed.add_field(name="Usage:", value="!remove [request_ID]")
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send('You do not have permission to use this command.')

        if message.content.startswith("!makerequest"):
            if is_board or is_bot_master:
                comma_message = message.content.replace('!makerequest', '').split(',')
                if len(comma_message) == 6:
                    manually_write_request(comma_message)
                    await message.channel.send('Request created!')
                else:
                    embed = Embed(title='!makerequest', description='Allows you to manually make a request')
                    embed.add_field(name="Usage:",
                                    value="!makerequest [name],[grade],[day],[time],[subject],[username]")
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send("You do not have permission to use this command.")

        if message.content.startswith('!commands'):
            embed = Embed(title='Help menu', description='Shows a list of commands')
            embed.add_field(name='!accept [request ID]', value='Allows you to accept a request')
            embed.add_field(name='!info [request ID]', value='Shows you information about a specific request')
            embed.add_field(name='!myrequests', value='Shows you all of the requests you\'ve accepted')
            embed.add_field(name='!list', value='Shows you a list of every (unaccepted and accepted) request')
            embed.add_field(name='!unaccept [request ID]', value='Allows you to unaccept a request')
            embed.add_field(name='!remove [request ID]', value='Allows you to remove a request entirely')
            await message.channel.send(embed=embed)



client.run('--------')
