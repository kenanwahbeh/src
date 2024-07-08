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
    else:

        user_type = result[0]  # استرجاع user_type من النتيجة
        return user_type

def upload_file(file_id,course_id,unit_id,type_id):
    try:
        cursor.execute('''
        INSERT INTO files (file_id, course_id, unit_id, type_id)
        VALUES (?, ?, ?, ?)
        ''', (file_id, course_id, unit_id, type_id))
        conn.commit()
        return 200
    except:
        return 400

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:#امر ابدا
    user = update.message.from_user
    chat_id = update.message.chat_id
    #التاكد من حفظ المستخدم
    user_type = save_user(user.username, user.first_name, user.last_name, chat_id)
    #فتح خيار جديد او حذف الخيارات السابقة
    context.user_data["course"] = ""
    context.user_data["unit"] = ""
     
    context.user_data["user_type"] = user_type
    context.user_data["upload"] = 0
    cursor.execute('SELECT list_name FROM lists')# استرجاع كل الصفوف كقائمة من التعابير
    lists = cursor.fetchall()
    #الرد على امر ابدا
    lists_list = [row[0] for row in lists]
    # تحويل lists_list إلى keyboard بالشكل المطلوب
    keyboard = [[(list_name)] for list_name in lists_list]
    if context.user_data["user_type"] == 1:
        keyboard.append(['upload'])
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
        "بماذا تريد ان اساعدك اليوم؟",
        reply_markup=markup,
    )
    print("course", context.user_data["course"] )
    print("unit", context.user_data["unit"])
    
    print("user_type", context.user_data["user_type"])
    print("upload", context.user_data["upload"])
    print("--------------- start_callback ---------------")
    return CHOOSING

async def upload_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الرسائل

    context.user_data["upload"] = 1
    await update.message.reply_text(
        "انت في وضع التحميل\n",

    )
    print("course", context.user_data["course"] )
    print("unit", context.user_data["unit"])
    
    print("user_type", context.user_data["user_type"])
    print("upload", context.user_data["upload"])
    print("--------------- upload_callback ---------------")
    return CHOOSING

async def courses_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الكورسات
    text = update.message.text
    context.user_data["course"] = ""
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
    print("course", context.user_data["course"] )
    print("unit", context.user_data["unit"])
    
    print("user_type", context.user_data["user_type"])
    print("upload", context.user_data["upload"])
    print("--------------- course_callback ---------------")
    return COURSES

async def units_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الوحدات
    context.user_data["unit"] = ""
    text = update.message.text
    cursor.execute('SELECT id FROM courses WHERE course_name = ?', (text,))
    result = cursor.fetchone()
    if context.user_data["upload"] != 1 and not result:
        context.user_data["course"] = ""
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
            "يوجد خطا في اسم المساق او المساق غير موجود\n"
            "الرجاء الاختيار من القائمة فقط او اضغط على /start\n"
            "الرجاء اختيار المساق المطلوب",
            reply_markup=markup,)
        print("course", context.user_data["course"] )
        print("unit", context.user_data["unit"])
        
        print("user_type", context.user_data["user_type"])
        print("upload", context.user_data["upload"])
        print("--------------- unit1_callback ---------------")
        return COURSES
    else:
        course_id = result[0]
        context.user_data["course"] =  course_id
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
        
        print("course", context.user_data["course"] )
        print("unit", context.user_data["unit"])
        
        print("user_type", context.user_data["user_type"])
        print("upload", context.user_data["upload"])
        print("--------------- unit2_callback ---------------")
        return UNITS
    
async def type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر الانواع
    
    text = update.message.text
    cursor.execute('SELECT id FROM units WHERE unit_number = ?', (text,))
    result = cursor.fetchone()
    if context.user_data["upload"] != 1 and not result:
        context.user_data["course"] = ""
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
            "يوجد خطا في اسم الوحدة او الوحدة غير موجودة\n"
            "الرجاء الاختيار من القائمة فقط او اضغط على /start\n"
            "الرجاء اختيارالوحدة - الاسبوع المطلوب",
            reply_markup=markup,)
        print("course", context.user_data["course"] )
        print("unit", context.user_data["unit"])
        
        print("user_type", context.user_data["user_type"])
        print("upload", context.user_data["upload"])
        print("--------------- type1_callback ---------------")
        return UNITS
    else:
        unit_id = result[0]
        context.user_data["unit"] =  unit_id
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
        print("course", context.user_data["course"] )
        print("unit", context.user_data["unit"])
        
        print("user_type", context.user_data["user_type"])
        print("upload", context.user_data["upload"])
        print("--------------- type2_callback ---------------")
        return FILE

async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:# امر رفع تزيل الملفات
    upload = context.user_data["upload"]
    user_type = context.user_data["user_type"]
    course_id =  context.user_data["course"] 
    unit_id =  context.user_data["unit"]
    text = update.message.text
    cursor.execute('SELECT id FROM types WHERE type_name = ?', (text,))
    result = cursor.fetchone()
    type_id = result[0]
    if upload == 1 and user_type == 1 :
        document = update.message.document
        if document:
            file_id = document.file_id
            upload_status = upload_file(file_id,course_id,unit_id,type_id)
            if upload_status == 200:
                await update.message.reply_text(
                    "تم الاضافة بنجاح\n"
                    "انقر هنا للغاء وضع المطور /start",)
            else:
                await update.message.reply_text(
                    "لم يتم اضافة الملف\n"
                    "انقر هنا للغاء وضع المطور /start",)
            return FILE
        else:
            await update.message.reply_text(
                    "ارسل الملف \n"
                    "انقر هنا للغاء وضع المطور /start",)
            return FILE 
    else:
        if type_id:
            
            cursor.execute('SELECT type_name FROM types')# استرجاع كل الصفوف كقائمة من التعابير
            types = cursor.fetchall()
            #الرد على امر ابدا
            types_list = [row[0] for row in types]
            # تحويل units_list إلى keyboard بالشكل المطلوب
            keyboard = [types_list[i:i+2] for i in range(0, len(types_list), 2)]
            keyboard.append(['Back'])
            keyboard.append(["Done"])
            markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                "مرحبا, انا مساعدك في التعلم في جامعة الشعب\n"
                "يوجد خطا الطلب\n"
                "الرجاء الاختيار من القائمة فقط او اضغط على /start\n"
                "الرجاء اختيار المطلوب",
                reply_markup=markup,)
            print("course", context.user_data["course"] )
            print("unit", context.user_data["unit"])
            
            print("user_type", context.user_data["user_type"])
            print("upload", context.user_data["upload"])
            print("--------------- file1_callback ---------------")
            return FILE
        else:
            # تنفيذ استعلام يحتوي على شروط متعددة
            cursor.execute('SELECT file_id FROM files WHERE course_id = ? AND unit_id = ? AND type_id = ?', (file_id,course_id,unit_id,type_id))

            # استرجاع النتائج
            results = cursor.fetchall()
            print(results)
            for result in results:
                file_id = result[0]
                await update.message.reply_document(document=file_id)
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
            print("course", context.user_data["course"] )
            print("unit", context.user_data["unit"])
            
            print("user_type", context.user_data["user_type"])
            print("upload", context.user_data["upload"])
            print("--------------- type2_callback ---------------")
            return FILE


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_callback)],
        states={
            CHOOSING: [
                CommandHandler("start", start_callback),
                MessageHandler(filters.Regex("^upload$"), upload_change),
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