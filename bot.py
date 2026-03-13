import random
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8696029054:AAEniGmR-oX93f5RDGCWfMfcr2zh7tF6GNQ"
ADMIN_ID = 8626918981

otp_group_link = "https://t.me/yourgroup"

# ---------------- DATABASE ----------------

db = sqlite3.connect("bot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
balance INTEGER DEFAULT 0
)
""")

db.commit()

# ---------------- SERVICES ----------------

services = ["Facebook","Telegram","TikTok"]

# ---------------- SERVICE COUNTRIES ----------------

service_countries = {
"Facebook":{"🇧🇩 Bangladesh":"+880"},
"Telegram":{"🇮🇹 Italy":"+39"},
"TikTok":{
"🇧🇩 Bangladesh":"+880",
"🇦🇴 Angola":"+244"
}
}

# ---------------- REAL NUMBER GENERATOR ----------------

def generate_number(prefix):

    if prefix == "+880":
        operators=["17","18","19","16","15","13"]
        op=random.choice(operators)
        number="".join(str(random.randint(0,9)) for _ in range(8))
        return f"+880{op}{number}"

    elif prefix == "+39":
        number="".join(str(random.randint(0,9)) for _ in range(9))
        return f"+393{number}"

    elif prefix == "+244":
        number="".join(str(random.randint(0,9)) for _ in range(8))
        return f"+2449{number}"

    else:
        number="".join(str(random.randint(0,9)) for _ in range(10))
        return f"{prefix}{number}"

# ---------------- FORCE JOIN ----------------

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user=update.effective_user.id

    if user==ADMIN_ID:
        return True

    if not otp_group_link:
        return True

    group=otp_group_link.split("/")[-1]

    try:
        member=await context.bot.get_chat_member(f"@{group}",user)

        if member.status in ["member","administrator","creator"]:
            return True

        return False

    except:
        return False

# ---------------- USER MENU ----------------

user_keyboard=[
["📱 Get Number","📊 Status"],
["👥 Invite Friends","💰 Withdraw"],
["☎ Support"]
]

user_menu=ReplyKeyboardMarkup(user_keyboard,resize_keyboard=True)

# ---------------- ADMIN MENU ----------------

admin_keyboard=[
["📊 Total Users","📢 Broadcast"],
["🌍 Countries","➕ Add Country"],
["❌ Delete Country","📱 User Menu"],
["➕ Add Service","❌ Delete Service"],
["🔗 Set OTP Group","❌ Delete OTP Group"]
]

admin_menu=ReplyKeyboardMarkup(admin_keyboard,resize_keyboard=True)

# ---------------- START ----------------

async def start(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user=update.effective_user.id

    joined=await check_join(update,context)

    if not joined:

        buttons=[
        [InlineKeyboardButton("🔗 Join Group",url=otp_group_link)],
        [InlineKeyboardButton("✅ Joined",callback_data="check_join")]
        ]

        keyboard=InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
        "⚠️ আগে OTP Group এ Join করুন",
        reply_markup=keyboard)

        return

    cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(user,))
    db.commit()

    await update.message.reply_text(
    "🤖 Premium Number Generator Bot",
    reply_markup=user_menu)

# ---------------- ADMIN ----------------

async def admin(update: Update,context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id!=ADMIN_ID:
        return

    await update.message.reply_text(
    "👑 Admin Dashboard",
    reply_markup=admin_menu)

# ---------------- BUTTON HANDLER ----------------

async def buttons(update: Update,context: ContextTypes.DEFAULT_TYPE):

    global otp_group_link

    text=update.message.text
    user=update.effective_user.id

    joined=await check_join(update,context)

    if not joined:

        buttons=[
        [InlineKeyboardButton("🔗 Join Group",url=otp_group_link)],
        [InlineKeyboardButton("✅ Joined",callback_data="check_join")]
        ]

        keyboard=InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
        "⚠️ আগে OTP Group এ Join করুন",
        reply_markup=keyboard)

        return

# ---------- USER ----------

    if text=="📱 Get Number":

        buttons=[]

        for s in services:
            buttons.append([InlineKeyboardButton(s,callback_data=f"service_{s}")])

        keyboard=InlineKeyboardMarkup(buttons)

        await update.message.reply_text("📱 Select Service",reply_markup=keyboard)

    elif text=="📊 Status":

        cursor.execute("SELECT balance FROM users WHERE user_id=?",(user,))
        bal=cursor.fetchone()[0]

        await update.message.reply_text(f"📊 Balance : {bal}")

    elif text=="👥 Invite Friends":

        link=f"https://t.me/{context.bot.username}?start={user}"

        await update.message.reply_text(f"Invite Link:\n{link}")

    elif text=="💰 Withdraw":

        await update.message.reply_text("Send withdraw request to admin.")

    elif text=="☎ Support":

        await update.message.reply_text("Contact Admin")

# ---------- ADMIN ----------

    elif text=="📊 Total Users" and user==ADMIN_ID:

        cursor.execute("SELECT COUNT(*) FROM users")
        total=cursor.fetchone()[0]

        await update.message.reply_text(f"👥 Total Users : {total}")

    elif text=="📢 Broadcast" and user==ADMIN_ID:

        context.user_data["broadcast"]=True
        await update.message.reply_text("Send Broadcast Message")

    elif context.user_data.get("broadcast") and user==ADMIN_ID:

        context.user_data["broadcast"]=False

        cursor.execute("SELECT user_id FROM users")
        users=cursor.fetchall()

        for u in users:
            try:
                await context.bot.send_message(u[0],text)
            except:
                pass

        await update.message.reply_text("Broadcast Sent")

# ---------- COUNTRIES ----------

    elif text=="🌍 Countries" and user==ADMIN_ID:

        msg=""

        for s in service_countries:

            msg+=f"\n{s}\n"

            for c in service_countries[s]:
                code=service_countries[s][c]
                msg+=f"{c} {code}\n"

        await update.message.reply_text(msg)

# ---------- ADD COUNTRY ----------

    elif text=="➕ Add Country" and user==ADMIN_ID:

        context.user_data["add_country"]=True
        await update.message.reply_text(
        "Send:\nService Country Code\nExample:\nTelegram 🇧🇩 Bangladesh +880")

    elif context.user_data.get("add_country") and user==ADMIN_ID:

        try:

            parts=text.split()

            service=parts[0]
            name=" ".join(parts[1:-1])
            code=parts[-1]

            if service not in service_countries:
                service_countries[service]={}

            service_countries[service][name]=code

            context.user_data["add_country"]=False

            await update.message.reply_text("Country Added")

        except:
            await update.message.reply_text("Format Error")

# ---------- DELETE COUNTRY ----------

    elif text=="❌ Delete Country" and user==ADMIN_ID:

        buttons=[]

        for service in service_countries:
            buttons.append([InlineKeyboardButton(service,callback_data=f"delcountry_{service}")])

        keyboard=InlineKeyboardMarkup(buttons)

        await update.message.reply_text("Select Service",reply_markup=keyboard)

# ---------- ADD SERVICE ----------

    elif text=="➕ Add Service" and user==ADMIN_ID:

        context.user_data["add_service"]=True
        await update.message.reply_text("Send Service Name")

    elif context.user_data.get("add_service") and user==ADMIN_ID:

        if text not in services:

            services.append(text)
            service_countries[text]={}

        context.user_data["add_service"]=False

        await update.message.reply_text("Service Added")

# ---------- DELETE SERVICE ----------

    elif text=="❌ Delete Service" and user==ADMIN_ID:

        buttons=[]

        for s in services:
            buttons.append([InlineKeyboardButton(s,callback_data=f"delservice_{s}")])

        keyboard=InlineKeyboardMarkup(buttons)

        await update.message.reply_text("Select Service",reply_markup=keyboard)

# ---------- SET OTP GROUP ----------

    elif text=="🔗 Set OTP Group" and user==ADMIN_ID:

        context.user_data["set_group"]=True
        await update.message.reply_text("Send OTP Group Link")

    elif context.user_data.get("set_group") and user==ADMIN_ID:

        otp_group_link=text
        context.user_data["set_group"]=False

        await update.message.reply_text("OTP Group Updated")

# ---------- DELETE OTP GROUP ----------

    elif text=="❌ Delete OTP Group" and user==ADMIN_ID:

        otp_group_link=""
        await update.message.reply_text("OTP Group Deleted")

# ---------- USER MENU ----------

    elif text=="📱 User Menu" and user==ADMIN_ID:

        await update.message.reply_text("User Menu",reply_markup=user_menu)

# ---------------- CALLBACK ----------------

async def callback(update: Update,context: ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    data=query.data
    await query.answer()

# ---------- SERVICE ----------

    if data.startswith("service_"):

        service=data.replace("service_","")

        context.user_data["service"]=service

        buttons=[]

        for c in service_countries.get(service,{}):
            buttons.append([InlineKeyboardButton(c,callback_data=f"country_{c}")])

        keyboard=InlineKeyboardMarkup(buttons)

        await query.message.edit_text("🌍 Select Country",reply_markup=keyboard)

# ---------- COUNTRY ----------

    elif data.startswith("country_"):

        await query.message.delete()

        country=data.replace("country_","")

        service=context.user_data.get("service")

        prefix=service_countries[service][country]

        number=generate_number(prefix)

        msg=f"""
🔄 New Number Generated

Service : {service}
Number : {number}

Country : {country}
OTP Status : Waiting for OTP
"""

        buttons=[
        [InlineKeyboardButton("🔄 Change Number",callback_data=f"change_{country}")],
        [InlineKeyboardButton("👁 View OTP Group",url=otp_group_link)]
        ]

        keyboard=InlineKeyboardMarkup(buttons)

        await query.message.reply_text(msg,reply_markup=keyboard)

# ---------- CHANGE NUMBER ----------

    elif data.startswith("change_"):

        country=data.replace("change_","")

        service=context.user_data.get("service")

        prefix=service_countries[service][country]

        number=generate_number(prefix)

        msg=f"""
🔄 New Number Generated

Service : {service}
Number : {number}

Country : {country}
OTP Status : Waiting for OTP
"""

        buttons=[
        [InlineKeyboardButton("🔄 Change Number",callback_data=f"change_{country}")],
        [InlineKeyboardButton("👁 View OTP Group",url=otp_group_link)]
        ]

        keyboard=InlineKeyboardMarkup(buttons)

        await query.message.edit_text(msg,reply_markup=keyboard)

# ---------- DELETE SERVICE CALLBACK ----------

    elif data.startswith("delservice_"):

        service=data.replace("delservice_","")

        if service in services:

            services.remove(service)
            del service_countries[service]

        await query.message.edit_text(f"{service} Deleted")

# ---------- DELETE COUNTRY CALLBACK ----------

    elif data.startswith("delcountry_"):

        service=data.replace("delcountry_","")

        buttons=[]

        for c in service_countries.get(service,{}):
            buttons.append([InlineKeyboardButton(c,callback_data=f"delc_{service}_{c}")])

        keyboard=InlineKeyboardMarkup(buttons)

        await query.message.edit_text("Select Country To Delete",reply_markup=keyboard)

    elif data.startswith("delc_"):

        _,service,country=data.split("_",2)

        if country in service_countries.get(service,{}):
            del service_countries[service][country]

        await query.message.edit_text(f"{country} Deleted")

# ---------------- RUN BOT ----------------

app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("admin",admin))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,buttons))
app.add_handler(CallbackQueryHandler(callback))

print("Bot Running...")
app.run_polling()
