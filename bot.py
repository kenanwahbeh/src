import logging
from typing import Dict
from keyboards import main_keyboard, courses_keyboard,all_index
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
TOKEN = '7342771029:AAF2JQrzZ5MjHr3A1DNb0_AsATVFBjd0p44'
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)





logger = logging.getLogger(__name__)
CHOOSING, COURSES, UNITS,TYPE, FILE = range(5)

def save_user(username, first_name, last_name, chat_id):
    cursor.execute('SELECT user_type FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    if not result:#اذا كان المستخدم غير موجود
        cursor.execute('''
        INSERT INTO users (username, first_name, last_name, chat_id)
        VALUES (?, ?, ?, ?)
        ''', (username, first_name, last_name, chat_id))
        conn.commit()
        user_type = 0
        return user_type
    else:

        user_type = result[0]  # استرجاع user_type من النتيجة
        return user_type

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:#امر ابدا
    user = update.message.from_user
    chat_id = update.message.chat_id
    #التاكد من حفظ المستخدم
    user_type = save_user(user.username, user.first_name, user.last_name, chat_id)
    #فتح خيار جديد او حذف الخيارات السابقة
    context.user_data["course_id"] = ""
    context.user_data["unit_id"] = ""
    context.user_data["type_id"] = ""
    context.user_data["user_type"] = user_type
    context.user_data["developer"] = 0
    cursor.execute('SELECT list_name FROM lists')# استرجاع كل الصفوف كقائمة من التعابير
    lists = cursor.fetchall()
    #الرد على امر ابدا
    lists_list = [row[0] for row in lists]
    # تحويل lists_list إلى keyboard بالشكل المطلوب
    keyboard = [[(list_name)] for list_name in lists_list]
    if context.user_data["user_type"] == 1:
        keyboard.append(['Developer'])
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
        "بماذا تريد ان اساعدك اليوم؟",
        reply_markup=markup,
    )
    return CHOOSING

async def developer_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الرسائل
    context.user_data["developer"] = 1
    await update.message.reply_text(
        "انت في وضع التحميل\n",)
    return CHOOSING

async def courses_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الكورسات
    cursor.execute('SELECT course_name FROM courses')# استرجاع كل الصفوف كقائمة من التعابير
    courses = cursor.fetchall()
    #الرد على امر ابدا
    courses_list = [row[0] for row in courses]
    # تحويل courses_list إلى keyboard بالشكل المطلوب
    keyboard = [courses_list[i:i+2] for i in range(0, len(courses_list), 2)]
    keyboard.append(['Back'])
    keyboard.append(["Done"])
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
        "الرجاء اختيار المساق المطلوب",
        reply_markup=markup,)
    return COURSES

async def units_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الوحدات
    text = update.message.text
    cursor.execute('SELECT id FROM courses WHERE course_name = ?', (text,))
    result = cursor.fetchone()
    if context.user_data["developer"] != 1 and not result:
        await courses_callback(update, context)
        return COURSES
    else:
        course_id = result[0]
        context.user_data["course_id"] =  course_id
        cursor.execute('SELECT unit_number FROM units')# استرجاع كل الصفوف كقائمة من التعابير
        units = cursor.fetchall()
        #الرد على امر ابدا
        units_list = [row[0] for row in units]
        # تحويل units_list إلى keyboard بالشكل المطلوب
        keyboard = [units_list[i:i+2] for i in range(0, len(units_list), 2)]
        keyboard.append(['Back'])
        keyboard.append(["Done"])
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
            "الرجاء اختيار الاسبوع - الوحدة",
            reply_markup=markup,)
        return UNITS
    
async def type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الانواع
    text = update.message.text
    cursor.execute('SELECT id FROM units WHERE unit_number = ?', (text,))
    result = cursor.fetchone()
    if context.user_data["developer"] != 1 and not result:
        await units_callback(update, context)
        return UNITS
    else:
        unit_id = result[0]
        context.user_data["unit_id"] =  unit_id
        cursor.execute('SELECT type_name FROM types')# استرجاع كل الصفوف كقائمة من التعابير
        types = cursor.fetchall()
        #الرد على امر ابدا
        types_list = [row[0] for row in types]
        # تحويل types_list إلى keyboard بالشكل المطلوب
        keyboard = [types_list[i:i+2] for i in range(0, len(types_list), 2)]
        keyboard.append(['Back'])
        keyboard.append(["Done"])
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
            "الرجاء الاختيار من القائمة",
            reply_markup=markup,)
        return FILE

async def developer_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    document = update.message.document
    photo = update.message.photo
    video = update.message.video
    course_id = context.user_data["course_id"]
    unit_id = context.user_data["unit_id"]
    type_id = context.user_data["type_id"]
    if text:
        cursor.execute('SELECT id FROM types WHERE type_name = ?', (text,))
        result = cursor.fetchone()
        if result:
            type_id = result[0]
            context.user_data["type_id"] = type_id
            await update.message.reply_text(
                "تم اختيار النوع بنجاح ارسل الملف او\n"
                "انقر هنا للغاء وضع المطور /start",)
        else:
            file_type = 'TXT'
            cursor.execute('''
            INSERT INTO files (file_id, course_id, unit_id, type_id,file_type)
            VALUES (?, ?, ?, ?, ?)
            ''', (text, course_id, unit_id, type_id,file_type))
            conn.commit()
            await update.message.reply_text(
            "تم اضافة النص بنجاح\n"
            "انقر هنا للغاء وضع المطور /start",)
    else:        

        if document or photo or video:
            if type_id == "":# اذا لم يتم اختيار النوع
                await update.message.reply_text(
                    "يجب اختيار النوع\n"
                    "انقر هنا للغاء وضع المطور /start",)
            else:
                if document:
                    file_id = document.file_id
                    file_type = 'DOC'
                elif photo:
                    file_id = photo[-1].file_id
                    file_type = 'PHO'
                elif video:
                    file_id = video.file_id
                    file_type = 'VID'
                try:
                    cursor.execute('''
                    INSERT INTO files (file_id, course_id, unit_id, type_id,file_type)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (file_id, course_id, unit_id, type_id,file_type))
                    conn.commit()
                    await update.message.reply_text(
                    "تم اضافة العنصر بنجاح\n"
                    "انقر هنا للغاء وضع المطور /start",)
                except:
                    await update.message.reply_text(
                    "حدث خطا عند الاضافة لن يتم اضافة العنصر\n"
                    "انقر هنا للغاء وضع المطور /start",)
        else:
            await update.message.reply_text(
                "النوع غير معروف الرجاء اختيار عنصر معرف \n"
                "انقر هنا للغاء وضع المطور /start",)

    return FILE 

async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر رفع تزيل الملفات
    developer = context.user_data["developer"]
    user_type = context.user_data["user_type"]
    if developer == 1 and user_type == 1 :
        await developer_tools(update, context)
        return FILE
    else:
        text = update.message.text
        cursor.execute('SELECT id FROM types WHERE type_name = ?', (text,))
        result = cursor.fetchone()
        if not result:
            await type_callback(update, context)
            return TYPE
        else:
            type_id = result[0]
            course_id =  context.user_data["course_id"] 
            unit_id =  context.user_data["unit_id"]
            cursor.execute('SELECT file_id, file_type FROM files WHERE course_id = ? AND unit_id = ? AND type_id = ?', (course_id,unit_id,type_id))
            results = cursor.fetchall()
            for result in results:
                file_id = result[0]
                file_type = result[1]
                if file_type == "DOC":
                    await update.message.reply_document(document=file_id)
                elif file_type == "PHO":
                    await update.message.reply_photo(photo=file_id)
                elif file_type == "VID":
                    await update.message.reply_video(video=file_id)
                elif file_type == "TXT":
                    await update.message.reply_text(text=file_id)
            await type_callback(update, context)
            return TYPE

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_callback)],
        states={
            CHOOSING: [
                CommandHandler("start", start_callback),
                MessageHandler(filters.Regex("^Developer$"), developer_active),
                MessageHandler(filters.Regex("^مساقات$"), courses_callback),
                MessageHandler(filters.Regex("^Back$"), start_callback),
                    # MessageHandler(
                #     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
                # )
            ],
            COURSES: [
                CommandHandler("start", start_callback),
                MessageHandler(filters.Regex("^Back$"), start_callback),
                MessageHandler(filters.Regex("^Done$"), start_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND,units_callback),
            ],
            UNITS:[
                CommandHandler("start", start_callback),
                MessageHandler(filters.Regex("^Back$"), courses_callback),
                MessageHandler(filters.Regex("^Done$"), start_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND,type_callback),
            ],
            TYPE:[
                CommandHandler("start", start_callback),
                MessageHandler(filters.Regex("^Back$"), units_callback),
                MessageHandler(filters.Regex("^Done$"), start_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND,file_callback),
            ],
            FILE:[
                CommandHandler("start", start_callback),
                MessageHandler(filters.Document.ALL, file_callback),
                MessageHandler(filters.PHOTO, file_callback),
                MessageHandler(filters.VIDEO, file_callback),
                MessageHandler(filters.Regex("^Back$"), type_callback),
                MessageHandler(filters.Regex("^Done$"), start_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND,file_callback),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), start_callback)],
    )

    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()