from faker import Faker
import random
import json
from datetime import datetime

fake = Faker('pl_PL')  # Ustawienie lokalizacji na język polski

def generate_order_event(event_id):
    line_items = []
    num_items = random.randint(1, 5)
    for _ in range(num_items):
        item_id = fake.uuid4()
        offer_id = fake.uuid4().split('-')[0]
        quantity = random.randint(1, 3)
        price = round(random.uniform(20, 200), 2)
        
        line_items.append({
            'id': str(item_id),
            'offer': {
                'id': str(offer_id),
                'name': fake.word(ext_word_list=['Koszulka', 'Spodnie', 'Buty', 'Kurtka', 'Rękawiczki']),
                'external': {
                    'id': "AH-" + str(random.randint(10000, 99999))
                }
            },
            'quantity': quantity,
            'originalPrice': {
                'amount': str(price),
                'currency': 'PLN'
            },
            'price': {
                'amount': str(price),
                'currency': 'PLN'
            },
            'boughtAt': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z'
        })
    
    checkout_form = {
        'id': fake.uuid4(),
        'messageToSeller': fake.sentence(),
        'buyer': {
            'id': fake.uuid4(),
            'email': fake.email(),
            'login': fake.user_name(),
            'firstName': fake.first_name(),
            'lastName': fake.last_name(),
            'companyName': None,
            'guest': False,
            'personalIdentity': fake.ssn(),
            'phoneNumber': None,
            'preferences': {
                'language': 'pl-PL'
            },
            'address': {
                'street': fake.street_name(),
                'city': fake.city(),
                'postCode': fake.postcode(),
                'countryCode': 'PL'
            }
        },
        'payment': {
            'id': fake.uuid4(),
            'type': 'CASH_ON_DELIVERY',
            'provider': 'P24',
            'finishedAt': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
            'paidAmount': {
                'amount': line_items[0]['originalPrice']['amount'],
                'currency': 'PLN'
            },
            'reconciliation': {
                'amount': line_items[0]['originalPrice']['amount'],
                'currency': 'PLN'
            },
            'features': [
                'ALLEGRO_PAY'
            ]
        },
        'status': 'READY_FOR_PROCESSING',
        'fulfillment': {
            'status': random.choice(['NEW', 'PROCESSING','READY_FOR_SHIPMENT','READY_FOR_PICKUP','SENT','PICKED_UP','CANCELLED','SUSPENDED']),
            'shipmentSummary': {
                'lineItemsSent': 'SOME'
            }
        },
        'delivery': {
            'address': {
                'firstName': fake.first_name(),
                'lastName': fake.last_name(),
                'street': fake.street_name(),
                'city': fake.city(),
                'zipCode': fake.postcode(),
                'countryCode': 'PL',
                'companyName': None,
                'phoneNumber': None,
                'modifiedAt': None
            },
            'method': {
                'id': fake.uuid4(),
                'name': 'Allegro Paczkomaty InPost'
            },
            'pickupPoint': {
                'id': 'POZ08A',
                'name': 'Paczkomat POZ08A',
                'description': 'Stacja paliw BP',
                'address': {}
            },
            'cost': {
                'amount': line_items[0]['originalPrice']['amount'],
                'currency': 'PLN'
            },
            'time': {
                'from': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
                'to': fake.date_time_this_month(before_now=False, after_now=True, tzinfo=None).isoformat() + 'Z',
                'guaranteed': {
                    'from': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
                    'to': fake.date_time_this_month(before_now=False, after_now=True, tzinfo=None).isoformat() + 'Z'
                },
                'dispatch': {
                    'from': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
                    'to': fake.date_time_this_month(before_now=False, after_now=True, tzinfo=None).isoformat() + 'Z'
                }
            },
            'smart': True,
            'calculatedNumberOfPackages': 1
        },
        'invoice': {
            'required': True,
            'address': {
                'street': fake.street_name(),
                'city': fake.city(),
                'zipCode': fake.postcode(),
                'countryCode': 'PL',
                'company': {
                    'name': 'Udix Sp. z o.o.',
                    'taxId': None
                },
                'naturalPerson': {
                    'firstName': fake.first_name(),
                    'lastName': fake.last_name()
                }
            },
            'dueDate': fake.date_this_month(before_today=True, after_today=True).isoformat()
        },
        'lineItems': line_items,
        'surcharges': [
            {
                'id': fake.uuid4(),
                'type': 'CASH_ON_DELIVERY',
                'provider': 'P24',
                'finishedAt': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
                'paidAmount': {
                    'amount': line_items[0]['originalPrice']['amount'],
                    'currency': 'PLN'
                },
                'reconciliation': {
                    'amount': line_items[0]['originalPrice']['amount'],
                    'currency': 'PLN'
                },
                'features': [
                    'ALLEGRO_PAY'
                ]
            }
        ],
        'discounts': [
            {
                'type': 'COUPON'
            }
        ],
        'note': {
            'text': fake.sentence()
        },
        'marketplace': {
            'id': 'allegro-pl'
        },
        'summary': {
            'totalToPay': {
                'amount': line_items[0]['originalPrice']['amount'],
                'currency': 'PLN'
            }
        },
        'updatedAt': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z',
        'revision': fake.uuid4()
    }
    
    event = {
        'id': str(event_id),
        'order': {
            'seller': {
                'id': '437848322'
            },
            'buyer': {
                'id': fake.uuid4(),
                'email': fake.email(),
                'login': fake.user_name(),
                'guest': False,
                'preferences': {
                    'language': 'pl-PL'
                }
            },
            'lineItems': line_items,
            'checkoutForms': [checkout_form],
            'marketplace': {
                'id': 'allegro-pl'
            }
        },
        'type': 'READY_FOR_PROCESSING',
        'occurredAt': fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None).isoformat() + 'Z'
    }
    
    return event

# Generowanie 10 obiektów
events = []
for i in range(10):
    events.append(generate_order_event(i))

# Zapisanie wynikowego JSON do pliku
with open('sample_order_events.json', 'w', encoding='utf-8') as f:
    json.dump({'events': events}, f, ensure_ascii=False, indent=4)

print("Wygenerowano 10 obiektów i zapisano je do pliku 'sample_order_events.json'")
