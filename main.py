import string
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple
import httpx
import matplotlib.pyplot as plt

def get_text(url: str) -> Optional[str]:
    """
    Функція завантажує текст із заданої URL-адреси.
    """
    with httpx.Client() as client:
        response = client.get(url)
        if response.status_code == 200:
            return response.text
        return None

def remove_punctuation(text: str) -> str:
    """
    Видаляє пунктуацію з тексту.
    """
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word: str) -> Tuple[str, int]:
    """
    Функція відображення для MapReduce.
    """
    return word.lower(), 1

def shuffle_function(mapped_values: List[Tuple[str, int]]) -> Dict[str, List[int]]:
    """
    Функція групування значень за ключами.
    """
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled

def reduce_function(key_values: Tuple[str, List[int]]) -> Tuple[str, int]:
    """
    Функція зменшення для MapReduce.
    """
    key, values = key_values
    return key, sum(values)

def map_reduce(url: str, search_words: Optional[List[str]] = None) -> Optional[Dict[str, int]]:
    """
    Реалізація алгоритму MapReduce для аналізу частоти слів у тексті.
    """
    text = get_text(url)
    if text is None:
        print("Помилка завантаження тексту.")
        return None
    
    text = remove_punctuation(text)
    words = text.split()
    
    if search_words:
        words = [word for word in words if word.lower() in search_words]
    
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))
    
    shuffled_values = shuffle_function(mapped_values)
    
    with ThreadPoolExecutor() as executor:
        reduced_values = dict(executor.map(reduce_function, shuffled_values.items()))
    
    return reduced_values

def visualize_top_words(result: Dict[str, int]) -> None:
    """
    Візуалізує 10 найбільш вживаних слів у вигляді горизонтальної гістограми.
    """
    top_10 = Counter(result).most_common(10)
    labels, values = zip(*top_10)
    
    plt.figure(figsize=(10, 5))
    plt.barh(labels, values, color='g')
    plt.xlabel('Кількість')
    plt.ylabel('Слово')
    plt.title('10 найпопулярніших слів')
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    search_words = []
    result = map_reduce(url, search_words)
    
    if result:
        print("Результат підрахунку слів:", result)
        visualize_top_words(result)