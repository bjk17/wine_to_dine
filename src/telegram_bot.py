import os
import logging
from datetime import date, timedelta

from geopy.distance import distance
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackContext, \
    DispatcherHandlerStop, MessageHandler, Filters

from src.globalwinescore import GlobalWineScore
from src.systembolaget import SystembolagetAPI
from src.recommender import assign_scorings

logger = logging.getLogger("TelegramBot")
logging.getLogger().setLevel(logging.INFO)

START_MSG = (
    "Hi! You can use me find highly rated wines from Systembolaget. "
    "If you want to filter the recommendations by store availability, run"
    "\n\n```  /set_store <name>```\n\n"
    "where `<name>` is the name of the store you'll be visiting. "
    "You can also emit the store name and I will ask you for your "
    "location in order to find a nearby store for you.\n\n"
    "If you don't care about store availability, you can instead type"
    "\n\n```  /recommend_red_wines <max_price>```\n\n"
    "where `max_price` is an optional maximal price in SEK."
)

HELP_MSG = "\n".join((
    "/start - starts an interaction with the bot",
    "/set_store <store_name> - picks a preferred store to base suggestions on",
    "/clear_store - clears the preferred store",
    "/recommend_red_wines <max_price> - recommends top 5 red wines available",
    "/help - this message",
))


def start_cmd(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")
    update.message.reply_text(START_MSG, parse_mode='Markdown')


def help_cmd(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")
    update.message.reply_text(HELP_MSG)


def clear_store(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")

    try:
        store_name = context.chat_data.pop('store_name')
        update.message.reply_text(
            f"I cleared your preference of '{store_name}' and will now "
            f"suggest inventory items available online at Systembolaget.se",
            reply_markup=ReplyKeyboardRemove())
    except KeyError:
        update.message.reply_text(
            f"You had not chosen a specific store, but I'll keep suggesting "
            f"inventory items available online at Systembolaget.se",
            reply_markup=ReplyKeyboardRemove())


def set_store(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")

    if not context.args:
        update.message.reply_text(
            "Will you please share your location with me?",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton(text="Yes, share location",
                                request_location=True)],
                [KeyboardButton(text="No, not at this time")]
            ], one_time_keyboard=True))
        raise DispatcherHandlerStop

    store_name = " ".join(context.args)
    if store_name.lower() not in sites_as_dict:
        update.message.reply_text(
            f"Store name '{store_name}' not recognised, please try again.",
            reply_markup=ReplyKeyboardRemove())
        raise DispatcherHandlerStop

    site = sites_as_dict[store_name.lower()]
    context.chat_data['store_name'] = site['Name']

    update.message.reply_text(
        f"Great! Now I'm only going to suggest inventory items available at "
        f"'{site['Name']}'.", reply_markup=ReplyKeyboardRemove())
    update.message.reply_location(
        longitude=site['Position']['Long'], latitude=site['Position']['Lat'])

    opening_hours = {date.fromisoformat(item['Date'][:10]): item
                     for item in site['OpeningHours']}

    today = update.message['date'].date()
    tomorrow = today + timedelta(days=1)
    update.message.reply_text("Today ({}): {}\nTomorrow: {}".format(
        today,
        SystembolagetAPI.parse_opening_hours(opening_hours[today]),
        SystembolagetAPI.parse_opening_hours(opening_hours[tomorrow])
    ))


def handle_location(update, context: CallbackContext):
    logger.info(f"'location shared' by {update.message.from_user}")

    location = update.message.location
    nearest_sites = sorted(
        filter(lambda site: site.get('Position') is not None, sites),
        key=lambda site: distance(
            (location['longitude'], location['latitude']),
            (site['Position']['Long'], site['Position']['Lat'])
        ))

    rkm = ReplyKeyboardMarkup([
        [KeyboardButton(text=f"/set_store {nearest_sites[0]['Name']}")],
        [KeyboardButton(text=f"/set_store {nearest_sites[1]['Name']}")],
        [KeyboardButton(text=f"/set_store {nearest_sites[2]['Name']}")],
        [KeyboardButton(text=f"/set_store {nearest_sites[3]['Name']}")],
        [KeyboardButton(text="Cancel")]], one_time_keyboard=True)
    update.message.reply_text("Choose location", reply_markup=rkm)


def handle_text_responses(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")
    if update.message.text == 'Cancel' or update.message.text.startswith('No'):
        update.message.reply_text("All right, no problem.",
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(HELP_MSG)


def recommend_red_wines(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")
    recommendations = sorted_red_wine_matches
    N = 5

    max_price_msg = ""
    if context.args and context.args[0].isdecimal():
        max_price = int(context.args[0])
        max_price_msg = f" with max price of SEK {max_price}"
        recommendations = filter(
            lambda triple: int(triple[0].Price) <= max_price,
            recommendations)

    store_name = None
    if 'store_name' in context.chat_data:
        store_name = context.chat_data['store_name']
        recommendations = filter(
            lambda triple: triple[0].ProductNumber in store_products[store_name],
            recommendations)

    recommendations = list(recommendations)
    update.message.reply_text(
        "Top {} out of {} red wines available {}{}:".format(
            min(N, len(recommendations)), len(recommendations),
            f"at _{store_name}_" if store_name else "_online_",
            max_price_msg
        ), parse_mode='Markdown')

    for (inventory_item, certainty, scoring) in list(recommendations)[:N]:
        update.message.reply_text(
            f"[{inventory_item}]({inventory_item.get_url()}) "
            f"(SEK {int(inventory_item.Price)})\n"
            f"{scoring.score:.2f}% on GWS matching _'{scoring}'_ "
            f"({scoring.get_url()}) with {certainty}% certainty",
            parse_mode='Markdown')


def recommend_white_wines(update, context: CallbackContext):
    logger.info(f"cmd '{update.message.text}' by {update.message.from_user}")
    update.message.reply_text("Coming soon! Stay tuned :)")


SB_API_TOKEN = os.environ.get('SB_API_TOKEN')
sb = SystembolagetAPI(SB_API_TOKEN)

# Ensure fresh inventory status and opening hours
sb.clear_cache()

GWS_API_TOKEN = os.environ.get('GWS_API_TOKEN')
gws = GlobalWineScore(GWS_API_TOKEN)

# The bot runs as a process with objects staying in memory
logger.info("Pre-loading commonly accessed data")
sites = list(sb.get_sites())
sites_as_dict = {site['Name'].lower(): site for site in sites if site['Name']}
sid_to_name = {site['SiteId']: site['Name'] for site in sites}
store_products = {
    sid_to_name[item['SiteId']]: {p['ProductNumber'] for p in item['Products']}
    for item in sb.get_products_with_store() if item['SiteId'] in sid_to_name
}

logger.info("Pre-calculating red wine score matching")
sorted_red_wine_matches = sorted(
    assign_scorings(
        sb.get_red_wines(stock_required=True),
        gws.get_red_wines()
    ),
    key=lambda triple: triple[2].score,
    reverse=True
)

token = os.environ.get('TELEGRAM_TOKEN')
updater = Updater(token, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler('start', start_cmd))
dp.add_handler(CommandHandler('help', help_cmd))
dp.add_handler(CommandHandler('set_store', set_store))
dp.add_handler(CommandHandler('clear_store', clear_store))
dp.add_handler(CommandHandler('recommend_red_wines', recommend_red_wines))
dp.add_handler(CommandHandler('recommend_white_wines', recommend_white_wines))

dp.add_handler(MessageHandler(Filters.text, handle_text_responses))
dp.add_handler(MessageHandler(Filters.location, handle_location))

updater.start_polling()
logger.info("Bot is up and ready!")
updater.idle()
