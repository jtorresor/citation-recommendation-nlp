# Manual de Usuario - IntenCite

## 1. Introducción

IntenCite es una aplicación web que permite identificar automáticamente la función semántica que cumple una cita dentro de un texto académico.

El usuario proporciona un contexto de citación escrito en inglés, selecciona uno de los modelos disponibles y la aplicación devuelve:

- La función de citación predicha.
- El nivel de confianza de la predicción.
- La probabilidad asignada a cada una de las cinco categorías disponibles.
- El modelo utilizado para realizar la inferencia.

IntenCite funciona como una herramienta de apoyo para el análisis de literatura científica. Las predicciones generadas por los modelos no sustituyen la interpretación de un investigador.

---

## 2. Objetivo de la aplicación

IntenCite busca facilitar el análisis de literatura científica mediante la identificación automática de la función que desempeña una referencia dentro de un texto académico.

El sistema permite distinguir si una cita:

- Proporciona antecedentes o contexto.
- Evidencia un vacío de investigación.
- Corresponde a un método, herramienta o recurso utilizado por el trabajo citante.
- Es extendida, adaptada o mejorada.
- Se utiliza para establecer una comparación con otro trabajo.

La aplicación clasifica cada contexto en una de cinco funciones:

```text
Application
Background
Comparison
Gap
Improvement
```

---

## 3. Acceso a IntenCite

La aplicación puede utilizarse desde un despliegue en AWS o ejecutarse localmente mediante Docker.

### 3.1 Despliegue en AWS

Abra en un navegador la dirección proporcionada al finalizar el despliegue de IntenCite.

La dirección tendrá una estructura similar a:

```text
http://<nombre-del-alb>.us-east-1.elb.amazonaws.com
```

El Application Load Balancer distribuye automáticamente las solicitudes entre la interfaz web y la API de inferencia.

> La dirección pública puede cambiar si la infraestructura se destruye y posteriormente se vuelve a crear.

### 3.2 Ejecución local

Cuando IntenCite se ejecuta mediante Docker Compose, la aplicación puede abrirse en:

```text
http://localhost:8080
```

Este puerto corresponde al gateway local que dirige las solicitudes hacia la interfaz o hacia la API.

La API también puede consultarse directamente en:

```text
http://localhost:8001
```

La documentación interactiva de FastAPI está disponible en:

```text
http://localhost:8001/docs
```

---

## 4. Descripción de la interfaz

La pantalla principal de IntenCite contiene:

1. **Selector de modelo:** permite seleccionar el modelo que realizará la clasificación.
2. **Área de entrada:** permite ingresar el contexto académico que contiene la cita.
3. **Botón de clasificación:** envía el contexto seleccionado a la API.
4. **Categoría predicha:** muestra la función de citación identificada.
5. **Nivel de confianza:** muestra la probabilidad asignada a la categoría seleccionada.
6. **Distribución de probabilidades:** permite comparar las probabilidades de las cinco categorías.
7. **Pestañas de navegación:** permiten cambiar entre el análisis de citas y las estadísticas del corpus.

![Pantalla principal de IntenCite](assets/user/01-interfaz-principal.png)

La interfaz permite:

- Seleccionar el modelo activo en la esquina superior derecha.
- Cambiar entre **Análisis de Citas** y **Estadísticas del Corpus**.
- Ingresar un contexto de citación.
- Consultar la descripción de las cinco funciones de citación.
- Ejecutar la clasificación.
- Consultar la predicción y su distribución de probabilidades.

---

## 5. Selección del modelo

IntenCite permite seleccionar entre dos modelos.

### 5.1 TF-IDF + Logistic Regression

Corresponde al modelo supervisado utilizado como línea base del proyecto.

El modelo representa el texto mediante características TF-IDF y utiliza una regresión logística multiclase para seleccionar una de las cinco funciones de citación.

En la interfaz aparece como:

```text
TF-IDF + Logistic Regression
```

Su identificador interno es:

```text
tfidf-logreg-baseline-v1
```

Este modelo realiza inferencias rápidamente y resulta útil como punto de comparación frente al modelo basado en lenguaje.

### 5.2 Qwen2.5 1.5B + LoRA

El segundo modelo utiliza como base:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

y fue adaptado al problema mediante LoRA.

En la interfaz aparece como:

```text
Qwen2.5 1.5B + LoRA
```

Su identificador interno es:

```text
qwen2.5-1.5b-lora-3ctx
```

Este modelo requiere más recursos computacionales que el baseline.

La primera predicción después del inicio de la API puede tardar más debido a la carga del modelo en memoria. Las solicitudes posteriores normalmente son más rápidas porque el modelo permanece cargado dentro del proceso de la API.

> El tiempo de respuesta depende de los recursos disponibles, la longitud del contexto y el estado del servicio.

---

## 6. Cómo realizar una clasificación

### 6.1 Preparar el contexto

Seleccione un fragmento académico en inglés que contenga una cita o describa explícitamente la relación con un trabajo anterior.

Para obtener un resultado más interpretable:

- Incluya la oración completa donde aparece la cita.
- Incluya las oraciones anterior y posterior cuando aporten información útil.
- Evite ingresar únicamente un apellido, número de referencia o identificador.
- Compruebe que el fragmento permita interpretar cómo se utiliza el trabajo citado.

El texto debe:

- Tener entre 20 y 5000 caracteres.
- Contener al menos tres palabras.
- Estar preferiblemente escrito en inglés, debido al idioma de los datos utilizados durante el desarrollo de los modelos.

### 6.2 Seleccionar el modelo

Utilice el selector ubicado en la esquina superior derecha.

Seleccione:

```text
TF-IDF + Logistic Regression
```

o:

```text
Qwen2.5 1.5B + LoRA
```

El modelo seleccionado será utilizado en la siguiente solicitud de clasificación.

### 6.3 Ingresar el contexto

Pegue el fragmento en el campo:

```text
Paste the citation context here...
```

Por ejemplo:

```text
To improve the robustness of our citation classification system, we adopt the attention-based encoding method introduced by <cite>Johnson et al.</cite> and use their pretrained scientific language model as the feature extractor in our architecture.
```

### 6.4 Ejecutar la clasificación

Presione:

```text
Clasificar intención de cita
```

La interfaz enviará el contexto y el modelo seleccionado a:

```text
POST /api/v1/predict
```

Espere a que aparezca el resultado.

Cuando se utiliza Qwen2.5 + LoRA, la inferencia puede requerir varios segundos. Evite recargar la página mientras la solicitud se encuentra en ejecución.

### 6.5 Consultar el resultado

La interfaz presenta:

- Categoría predicha.
- Nivel de confianza.
- Distribución de probabilidades.
- Modelo utilizado.

![Resultado de una predicción con Qwen2.5 + LoRA](assets/user/03-ejemplo-analisis.png)

En el ejemplo mostrado, el modelo identifica una de las cinco funciones y presenta su confianza junto con las probabilidades obtenidas para las demás categorías.

La barra de mayor valor corresponde a la categoría seleccionada por el modelo.

Probabilidades cercanas entre varias categorías pueden indicar que el contexto presenta características compatibles con más de una función.

---

## 7. Categorías de clasificación

IntenCite utiliza cinco categorías.

| Categoría | Interpretación |
|---|---|
| **Application** | El trabajo citante utiliza una idea, método, recurso, herramienta o conjunto de datos proveniente del trabajo citado. |
| **Background** | La referencia proporciona antecedentes, conceptos o información general sobre el dominio o problema. |
| **Comparison** | El texto establece similitudes, diferencias o comparaciones entre el trabajo actual y el trabajo citado. |
| **Gap** | La referencia ayuda a evidenciar una limitación, necesidad o problema aún no resuelto. |
| **Improvement** | El trabajo citante extiende, adapta o modifica una idea o método presentado previamente. |

---

## 8. Ejemplos de contextos

### 8.1 Application

```text
We adopt the attention-based encoding method introduced by Smith et al. and use their pretrained model as the feature extractor in our architecture.
```

El texto indica explícitamente que el trabajo citante utiliza un método presentado anteriormente.

### 8.2 Background

```text
Previous studies have shown that citation analysis provides useful information about the structure and evolution of scientific disciplines.
```

La referencia proporciona contexto o conocimiento previo sobre el área.

### 8.3 Comparison

```text
Unlike the approach proposed by Johnson et al., our model does not require manually defined linguistic features.
```

El texto establece un contraste explícito con otro trabajo.

### 8.4 Gap

```text
Previous approaches achieve strong results, but they still fail to capture the rhetorical function of citations when the surrounding context is limited.
```

El fragmento describe una limitación que puede motivar un nuevo trabajo.

### 8.5 Improvement

```text
We extend the method introduced by Smith et al. by incorporating contextual embeddings and an additional attention layer.
```

El trabajo citante modifica o amplía un método existente.

> Los ejemplos ilustran las características generales de cada categoría. La categoría realmente obtenida dependerá de la inferencia realizada por el modelo seleccionado.

---

## 9. Interpretación de la confianza

La confianza corresponde a la probabilidad asignada por el modelo a la categoría seleccionada.

Por ejemplo, si el resultado muestra:

```text
Application
52.8%
```

significa que **Application** obtuvo la mayor probabilidad entre las cinco alternativas evaluadas.

Una confianza mayor indica que una categoría sobresale con mayor claridad frente a las demás según el modelo.

Sin embargo:

- Una confianza elevada no garantiza que la clasificación sea correcta.
- Una confianza baja no significa necesariamente que el resultado sea incorrecto.
- Probabilidades similares pueden indicar ambigüedad en el contexto.
- Diferentes modelos pueden generar distribuciones de probabilidad distintas para el mismo texto.

Las probabilidades no representan la calidad, importancia, veracidad o impacto del artículo citado.

---

## 10. Comparación de modelos

El usuario puede ejecutar el mismo contexto utilizando ambos modelos.

Esto permite observar cómo cambia:

- La categoría predicha.
- El nivel de confianza.
- La distribución entre las cinco categorías.
- El tiempo necesario para obtener una respuesta.

Los modelos tienen arquitecturas diferentes, por lo que no se espera que produzcan exactamente las mismas probabilidades.

TF-IDF + Logistic Regression utiliza características estadísticas del texto.

Qwen2.5 1.5B + LoRA utiliza un modelo de lenguaje adaptado específicamente a la tarea.

La comparación entre ambos modelos puede utilizarse con fines exploratorios, pero no debe interpretarse como una garantía individual de corrección.

---

## 11. Estadísticas del corpus

La pestaña **Estadísticas del Corpus** presenta información resumida sobre el conjunto de datos utilizado durante el proyecto.

![Estadísticas del corpus](assets/user/02-estadisticas-corpus.png)

La interfaz muestra:

| Métrica | Valor |
|---|---:|
| Contextos de citación | 3,491 |
| Pares citante-citado | 1,046 |
| Funciones de citación | 5 |
| Entrenamiento | 2,491 |
| Validación | 483 |
| Prueba | 517 |

La separación de los datos se realizó evitando que un mismo par entre artículo citante y artículo citado apareciera simultáneamente en diferentes particiones.

Las cinco clases utilizadas por IntenCite presentan una distribución aproximadamente balanceada dentro del corpus preparado para el proyecto.

---

## 12. Uso directo de la API

Además de la interfaz, IntenCite puede utilizarse mediante su API.

### 12.1 Consultar los modelos

```text
GET /api/v1/models
```

Ejemplo local:

```bash
curl http://localhost:8001/api/v1/models
```

La respuesta contiene los dos modelos disponibles.

### 12.2 Realizar una predicción con el baseline

```bash
curl -X POST "http://localhost:8001/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "We use the parser introduced by Smith et al. to preprocess all documents in our corpus.",
    "model": "tfidf-logreg-baseline-v1"
  }'
```

### 12.3 Realizar una predicción con Qwen2.5 + LoRA

```bash
curl -X POST "http://localhost:8001/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "To improve the robustness of our citation classification system, we adopt the attention-based encoding method introduced by <cite>Johnson et al.</cite> and use their pretrained scientific language model as the feature extractor in our architecture.",
    "model": "qwen2.5-1.5b-lora-3ctx"
  }'
```

Una respuesta presenta una estructura como:

```json
{
  "model": "qwen2.5-1.5b-lora-3ctx",
  "prediction": "Application",
  "confidence": 0.528,
  "probabilities": {
    "Application": 0.528,
    "Background": 0.142,
    "Comparison": 0.102,
    "Gap": 0.086,
    "Improvement": 0.142
  }
}
```

> Los valores del ejemplo son únicamente ilustrativos. Las probabilidades reales dependen del texto y del modelo utilizado.

### 12.4 Verificar la API

El estado básico puede consultarse mediante:

```text
GET /health
```

Ejemplo:

```bash
curl http://localhost:8001/health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

---

## 13. Mensajes y problemas frecuentes

### 13.1 El texto no puede enviarse

Compruebe que:

- El campo no esté vacío.
- El texto tenga al menos 20 caracteres.
- El fragmento contenga al menos tres palabras.
- El texto no exceda los 5000 caracteres.

### 13.2 La aplicación tarda en responder con Qwen2.5 + LoRA

El modelo Qwen requiere más recursos que TF-IDF + Logistic Regression.

La primera inferencia después de iniciar la API puede tardar más debido a la carga del modelo en memoria.

Espere a que termine la solicitud y evite presionar varias veces el botón de clasificación.

### 13.3 La aplicación no muestra resultados

Compruebe:

1. Que la página continúe abierta.
2. Que el servicio se encuentre disponible.
3. Que `/health` responda correctamente.
4. Si utiliza Docker local, que los contenedores estén activos.
5. Si el problema persiste, consulte los registros o informe al administrador.

### 13.4 La categoría parece incorrecta

Revise el contexto introducido.

Puede:

- Incluir la oración completa.
- Añadir las oraciones anterior y posterior.
- Verificar que el fragmento exprese claramente la relación con el trabajo citado.
- Probar el mismo contexto con el otro modelo.
- Revisar la distribución completa de probabilidades.

IntenCite es un prototipo académico y puede cometer errores.

### 13.5 Los dos modelos producen resultados diferentes

Este comportamiento es posible y no representa necesariamente un error.

Los modelos utilizan métodos de representación y clasificación distintos.

Revise:

- La categoría seleccionada.
- Las probabilidades completas.
- El contexto original.
- La definición de cada función de citación.

### 13.6 La dirección del despliegue no responde

La infraestructura puede encontrarse detenida o haber sido destruida después de las pruebas.

La dirección también puede haber cambiado después de un nuevo despliegue.

Solicite al administrador la URL actualmente activa.

---

## 14. Limitaciones

- Los modelos fueron desarrollados principalmente utilizando contextos académicos en inglés.
- IntenCite clasifica únicamente cinco funciones de citación.
- Un fragmento puede expresar más de una función aunque el sistema produzca una sola categoría principal.
- El desempeño puede disminuir en dominios, estilos de escritura o estructuras muy diferentes a los datos utilizados durante el entrenamiento.
- Los dos modelos pueden producir resultados distintos para un mismo contexto.
- La confianza del modelo no constituye una garantía de corrección.
- La clasificación no reemplaza la revisión humana del contenido académico.
- Qwen2.5 + LoRA requiere más tiempo y recursos de inferencia que el baseline.

---

## 15. Buenas prácticas

Para obtener resultados más interpretables:

- Utilice contextos académicos escritos en inglés.
- Incluya suficiente contexto alrededor de la cita.
- Evite fragmentos excesivamente cortos.
- Revise la distribución completa de probabilidades.
- Compare modelos cuando el caso sea ambiguo.
- Revise manualmente las clasificaciones importantes.
- No interprete la confianza como una medida de calidad del artículo citado.
- No utilice la clasificación como única evidencia para tomar decisiones académicas.