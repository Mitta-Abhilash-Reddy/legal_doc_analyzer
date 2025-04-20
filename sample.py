from googletrans import Translator

translator = Translator()
result = translator.translate("మీరు ఎలా ఉన్నారు?", src="te", dest="en")
print(result.text)