# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

#
NEWSLETTER_DB = ["weather", "bbc", "cnn", "sport", "travel", "tech"]


class ValidateNewsletterForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_newsletter_form"

    @staticmethod
    def newsletter_db() -> List[Text]:
        return NEWSLETTER_DB

    def validate_newsletter(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        newsletter = tracker.get_slot("newsletter")
        print(newsletter)
        if newsletter.lower() in self.newsletter_db():
            return {"newsletter": newsletter}
        else:
            dispatcher.utter_message(
                template="utter_not_in_channel", requested_newsletter=newsletter
            )
            return {"newsletter": None}


class AddNewsletterToSubscription(Action):
    def name(self) -> Text:
        return "action_newsletter_subscribed"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        newsletter = tracker.get_slot("newsletter")
        cart = tracker.get_slot("subscription_list")
        if cart is None:
            cart = []
        if newsletter is not None and {"newsletter": newsletter} in cart:
            dispatcher.utter_message(text="That's already added. ")

        if newsletter is not None and {"newsletter": newsletter} not in cart:
            cart.append({"newsletter": newsletter})

        if len(cart) > 0 and newsletter is not None:
            dispatcher.utter_message(
                template="utter_subscribed", newsletter=newsletter
            )

        return [SlotSet("subscription_list", cart),
                SlotSet("newsletter", None)]


class ShowSubscriptionList(Action):
    def name(self) -> Text:
        return "action_show_subscription_list"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        cart = tracker.get_slot("subscription_list")
        if cart is None or len(cart) == 0:
            dispatcher.utter_message(text="You have not yet subscribed to any newsletter.")
            return []
        condensed_cart = {}
        for item in cart:
            newsletter = item["newsletter"]
            condensed_cart[newsletter] = newsletter

        text = "Here is your subscription list:\n"
        for newsletter in condensed_cart.items():
            text += f"{newsletter}\n"
        text += "Enjoy!"
        dispatcher.utter_message(text=text)
        return []


class ShowChannels(Action):
    def name(self) -> Text:
        return "action_show_channels"

    @staticmethod
    def newsletter_db() -> List[Text]:
        return NEWSLETTER_DB

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        text = "Here are our available newsletter channel list:\n"
        for newsletter in self.newsletter_db():
            text += f"{newsletter}\n"
        text += "What seems to be interesting to you?"
        dispatcher.utter_message(text=text)
        return []
