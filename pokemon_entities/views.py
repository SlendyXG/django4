import folium

from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404, render

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(
        location=MOSCOW_CENTER,
        zoom_start=12,
        tiles='CartoDB positron',
    )

    now = localtime()
    for pokemon_entity in PokemonEntity.objects.all():
        if pokemon_entity.appeared_at and pokemon_entity.appeared_at > now:
            continue
        if pokemon_entity.disappeared_at and pokemon_entity.disappeared_at < now:
            continue

        pokemon = pokemon_entity.pokemon
        if pokemon.image:
            image_url = request.build_absolute_uri(pokemon.image.url)
        else:
            image_url = DEFAULT_IMAGE_URL
        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            image_url,
        )

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': request.build_absolute_uri(pokemon.image.url) if pokemon.image else DEFAULT_IMAGE_URL,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    now = localtime()

    folium_map = folium.Map(
        location=MOSCOW_CENTER,
        zoom_start=12,
        tiles='CartoDB positron',
    )

    entities = []
    for pokemon_entity in pokemon.pokemonentity_set.all():
        if pokemon_entity.appeared_at and pokemon_entity.appeared_at > now:
            continue
        if pokemon_entity.disappeared_at and pokemon_entity.disappeared_at < now:
            continue

        if pokemon.image:
            image_url = request.build_absolute_uri(pokemon.image.url)
        else:
            image_url = DEFAULT_IMAGE_URL

        add_pokemon(
            folium_map,
            pokemon_entity.lat,
            pokemon_entity.lon,
            image_url,
        )

        entities.append({
            'lat': pokemon_entity.lat,
            'lon': pokemon_entity.lon,
            'level': pokemon_entity.level,
            'health': pokemon_entity.health,
            'strength': pokemon_entity.strength,
            'defense': pokemon_entity.defense,
            'stamina': pokemon_entity.stamina,
            'appeared_at': pokemon_entity.appeared_at,
            'disappeared_at': pokemon_entity.disappeared_at,
        })

    if pokemon.image:
        img_url = request.build_absolute_uri(pokemon.image.url)
    else:
        img_url = DEFAULT_IMAGE_URL

    previous_evolution = None
    if pokemon.previous_evolution:
        prev = pokemon.previous_evolution
        previous_evolution = {
            'pokemon_id': prev.id,
            'title_ru': prev.title,
            'img_url': request.build_absolute_uri(prev.image.url) if prev.image else DEFAULT_IMAGE_URL,
        }

    next_evolution = None
    next_pokemon = pokemon.next_evolutions.first()
    if next_pokemon:
        next_evolution = {
            'pokemon_id': next_pokemon.id,
            'title_ru': next_pokemon.title,
            'img_url': request.build_absolute_uri(next_pokemon.image.url) if next_pokemon.image else DEFAULT_IMAGE_URL,
        }

    pokemon_on_page = {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'img_url': img_url,
        'description': pokemon.description,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,
        'entities': entities,
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_on_page,
    })