from models.venue import VenueModel

venue_list = [
    VenueModel(
        name="Cafe Aroma",
        location="Manama",
        max_capacity=30,
        avg_service_time=15,
        owner_id=1,
        image_url="https://fastly.picsum.photos/id/1060/400/300.jpg?hmac=wq6wnNRFBHc7MwFpOYYjGCtt9Eg9Ji3xu8Fe42HozO8"
    ),
    VenueModel(
        name="Tea House",
        location="Riffa",
        max_capacity=25,
        avg_service_time=10,
        owner_id=1,
        image_url="/images/tea_house.jpg"
    ),
    VenueModel(
        name="Latte Lounge",
        location="Muharraq",
        max_capacity=40,
        avg_service_time=12,
        owner_id=1,
        image_url="/images/latte_lounge.jpg"
    ),
    VenueModel(
        name="Coffee Corner",
        location="Isa Town",
        max_capacity=20,
        avg_service_time=8,
        owner_id=1,
        image_url="/images/coffee_corner.jpg"
    ),
    VenueModel(
        name="The Brew Spot",
        location="Juffair",
        max_capacity=35,
        avg_service_time=14,
        owner_id=1,
        image_url="/images/the_brew_spot.jpg"
    ),
]
