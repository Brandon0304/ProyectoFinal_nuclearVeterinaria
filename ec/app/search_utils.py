# Crear este archivo como ec/app/search_utils.py

def get_levenshtein_distance(s1, s2):
    """
    Calcula la distancia de Levenshtein entre dos cadenas.
    Esta métrica mide cuántos cambios (inserciones, eliminaciones o sustituciones)
    son necesarios para transformar una cadena en otra.
    """
    if len(s1) < len(s2):
        return get_levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def find_similar_terms(query_term, term_dict, threshold=2):
    """
    Encuentra términos similares al término de consulta basados en la distancia de Levenshtein.
    Devuelve el término más cercano si está dentro del umbral.
    """
    if query_term in term_dict:
        return query_term
    
    best_match = None
    best_distance = float('inf')
    
    for term in term_dict.keys():
        distance = get_levenshtein_distance(query_term, term)
        if distance < best_distance and distance <= threshold:
            best_distance = distance
            best_match = term
    
    return best_match

def get_query_suggestions(query, term_dict):
    """
    Genera sugerencias para una consulta basadas en términos similares.
    """
    query_words = query.lower().split()
    suggestions = []
    
    for word in query_words:
        similar_term = find_similar_terms(word, term_dict)
        if similar_term and similar_term != word:
            suggestion = query.replace(word, similar_term)
            suggestions.append(suggestion)
    
    return suggestions[:3]  # Limitar a 3 sugerencias