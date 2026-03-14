import json
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 30956542
API_HASH = "b36f49d94e7bb1109e22d7ee405d41b6"
BOT_TOKEN = "8457375768:AAGSQB3gnibvKgfvD5HB_e11Tbs5ybRf_TU"

ADMIN_ID = 8626918981
OTP_GROUP = "https://t.me/newottp24"

app = Client("otpbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# DATABASE
try:
    with open("data.json") as f:
        data = json.load(f)
except:
    data = {"services": {}}

users=set()

def save():
    with open("data.json","w") as f:
        json.dump(data,f)

admin_step = {}

# USER MENU
menu = ReplyKeyboardMarkup(
[
["📱 Get Number","📊 Status"],
["👥 Friend Invite","💰 Withdraw"],
["⭐ Premium User Only"],
["☎ Support"]
],
resize_keyboard=True
)

# START
@app.on_message(filters.command("start"))
async def start(client,message):

    users.add(message.from_user.id)

    await message.reply(
        "🤖 OTP BOT READY",
        reply_markup=menu
    )

# STATUS
@app.on_message(filters.command("status") | filters.regex("Status"))
async def status(client,message):

    services=len(data["services"])

    numbers=0
    for s in data["services"]:
        for c in data["services"][s]:
            numbers+=len(data["services"][s][c])

    await message.reply(f"""
📊 BOT STATUS

Services : {services}
Numbers : {numbers}

Bot Status : Online ✅
""")

# PREMIUM
@app.on_message(filters.regex("Premium"))
async def premium(client,message):

    await message.reply(
        "⭐ Premium User Only\n\n"
        "Premium নিতে যোগাযোগ করুন 👇\n"
        "https://t.me/skboy12344"
    )

# INVITE
@app.on_message(filters.regex("Invite"))
async def invite(client,message):

    bot=(await app.get_me()).username
    link=f"https://t.me/{bot}?start={message.from_user.id}"

    await message.reply(f"""
👥 Invite Friends

Your Invite Link:
{link}
""")

# SUPPORT
@app.on_message(filters.regex("Support"))
async def support(client,message):

    await message.reply("☎ Support\nContact Admin")

# WITHDRAW
@app.on_message(filters.regex("Withdraw"))
async def withdraw(client,message):

    await message.reply("💰 Withdraw System Coming Soon")

# ADMIN PANEL
@app.on_message(filters.command("admin"))
async def admin(client,message):

    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ You are not admin")

    panel = ReplyKeyboardMarkup(
    [
    ["➕ Add Service","🌍 Add Country"],
    ["📲 Add Number","📊 Bot Stats"],
    ["📦 Total Numbers","👤 Total Users"],
    ["❌ Delete Number"],
    ["⬅ Back"]
    ],
    resize_keyboard=True
    )

    await message.reply("👑 Admin Panel",reply_markup=panel)

# BACK
@app.on_message(filters.regex("Back"))
async def back(client,message):

    await message.reply("🔙 Back To Menu",reply_markup=menu)

# TOTAL USERS
@app.on_message(filters.regex("Total Users") & filters.user(ADMIN_ID))
async def total_users(client,message):

    await message.reply(f"👤 Total Users : {len(users)}")

# BOT STATS
@app.on_message(filters.regex("Bot Stats") & filters.user(ADMIN_ID))
async def botstats(client,message):

    services=len(data["services"])

    numbers=0
    for s in data["services"]:
        for c in data["services"][s]:
            numbers+=len(data["services"][s][c])

    await message.reply(f"""
📊 ADMIN STATS

Services : {services}
Numbers : {numbers}
""")

# TOTAL NUMBERS
@app.on_message(filters.regex("Total Numbers") & filters.user(ADMIN_ID))
async def totalnumbers(client,message):

    text="📦 NUMBERS\n\n"

    for s in data["services"]:
        for c in data["services"][s]:
            count=len(data["services"][s][c])
            text+=f"{s} - {c} : {count}\n"

    await message.reply(text)

# DELETE COUNTRY NUMBERS
@app.on_message(filters.regex("Delete Number") & filters.user(ADMIN_ID))
async def delete_number(client,message):

    admin_step[message.from_user.id]="delete_country"

    await message.reply(
        "Send format:\nservice country\n\nExample:\nwhatsapp pakistan"
    )

# ADD SERVICE
@app.on_message(filters.regex("Add Service") & filters.user(ADMIN_ID))
async def add_service(client,message):

    admin_step[message.from_user.id]="service"
    await message.reply("Send Service Name\nExample:\nwhatsapp")

# ADD COUNTRY
@app.on_message(filters.regex("Add Country") & filters.user(ADMIN_ID))
async def add_country(client,message):

    admin_step[message.from_user.id]="country"
    await message.reply("Send:\nservice country\nExample:\nwhatsapp pakistan")

# ADD NUMBER
@app.on_message(filters.regex("Add Number") & filters.user(ADMIN_ID))
async def add_number(client,message):

    admin_step[message.from_user.id]="number"
    await message.reply("Send format:\nservice country\nnumbers")

# ADMIN INPUT
@app.on_message(filters.text & filters.user(ADMIN_ID))
async def admin_input(client,message):

    step=admin_step.get(message.from_user.id)

    if step=="service":

        s=message.text.lower()

        if s not in data["services"]:
            data["services"][s]={}

        save()
        admin_step.pop(message.from_user.id)
        await message.reply("✅ Service Added")

    elif step=="country":

        s,c=message.text.lower().split()

        if s not in data["services"]:
            data["services"][s]={}

        if c not in data["services"][s]:
            data["services"][s][c]=[]

        save()
        admin_step.pop(message.from_user.id)
        await message.reply("✅ Country Added")

    elif step=="number":

        lines=message.text.split("\n")

        service,country=lines[0].split()
        numbers=lines[1:]

        if service not in data["services"]:
            data["services"][service]={}

        if country not in data["services"][service]:
            data["services"][service][country]=[]

        for n in numbers:
            data["services"][service][country].append(n)

        save()
        admin_step.pop(message.from_user.id)

        await message.reply(f"✅ {len(numbers)} Numbers Added")

    elif step=="delete_country":

        service,country=message.text.lower().split()

        if service in data["services"] and country in data["services"][service]:

            count=len(data["services"][service][country])

            data["services"][service][country]=[]

            save()

            await message.reply(f"❌ {count} numbers deleted from {service} {country}")

        else:
            await message.reply("❌ Service or country not found")

        admin_step.pop(message.from_user.id)

# GET NUMBER
@app.on_message(filters.regex("Get Number"))
async def get_number(client,message):

    buttons=[]

    for s in data["services"]:

        total=0
        for c in data["services"][s]:
            total+=len(data["services"][s][c])

        buttons.append(
        [InlineKeyboardButton(f"{s.title()} ({total})",callback_data=f"service|{s}")]
        )

    if len(buttons)==0:
        return await message.reply("❌ No Service Available")

    await message.reply(
        "🔧 Please select a service:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# SELECT SERVICE
@app.on_callback_query(filters.regex("service"))
async def service(client,call):

    service=call.data.split("|")[1]

    buttons=[]

    for c in data["services"][service]:

        count=len(data["services"][service][c])

        buttons.append(
        [InlineKeyboardButton(f"{c.title()} ({count})",callback_data=f"country|{service}|{c}")]
        )

    await call.message.edit(
        "🌍 Select Country",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# SELECT COUNTRY
@app.on_callback_query(filters.regex("country"))
async def country(client,call):

    _,service,country=call.data.split("|")

    numbers=data["services"][service][country]

    if len(numbers)==0:
        return await call.answer("❌ No numbers",True)

    number=numbers.pop(0)
    save()

    text=f"""
✅ New Number

Service : {service}
Number : {number}

Country : {country}
OTP Status : Waiting
"""

    buttons=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Change Number",callback_data=f"change|{service}|{country}")],
        [InlineKeyboardButton("👁 View OTP Group",url=OTP_GROUP)]
    ])

    await call.message.edit(text,reply_markup=buttons)

# CHANGE NUMBER
@app.on_callback_query(filters.regex("change"))
async def change(client,call):

    _,service,country=call.data.split("|")

    numbers=data["services"][service][country]

    if len(numbers)==0:
        return await call.answer("❌ No numbers left",True)

    number=numbers.pop(0)
    save()

    text=f"""
✅ New Number

Service : {service}
Number : {number}

Country : {country}
OTP Status : Waiting
"""

    buttons=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Change Number",callback_data=f"change|{service}|{country}")],
        [InlineKeyboardButton("👁 View OTP Group",url=OTP_GROUP)]
    ])

    await call.message.edit(text,reply_markup=buttons)

app.run()
