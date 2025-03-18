def grant_access_to_view_ticket(bot, message):
    markup = types.InlineKeyboardMarkup()
    markup.add(cancel)
    bot.send_message(message.chat.id, text="Укажите ID пользователя в Телеграм", reply_markup=markup)
    bot.register_next_step_handler(message, grant_access_to_view_ticket_follow_up)