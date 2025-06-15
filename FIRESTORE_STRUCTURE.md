# 🔥 Estructura de la Base de Datos Firestore - Proyecto Sumiller

## 📊 Esquema General

El proyecto Sumiller utiliza **Firebase Firestore** para la persistencia de datos del usuario y el historial de conversaciones. La base de datos está diseñada con una arquitectura simple y eficiente.

## 🗃️ Colecciones

### 1. **`users`** - Información de Usuarios

```javascript
// Documento: /users/{uid}
{
  uid: "google_auth_uid_123456",          // String - UID de Google Auth
  displayName: "Pedro García",             // String - Nombre completo
  email: "pedro@example.com",             // String - Email
  lastLogin: FirebaseTimestamp            // Timestamp - Último acceso
}
```

**Características:**
- **Document ID**: UID de Google Authentication
- **Propósito**: Almacenar información básica del usuario
- **Operaciones**: `setDoc` con `{ merge: true }` para actualizaciones
- **Índices**: Automáticos por Firestore

### 2. **`conversations`** - Historial de Conversaciones

```javascript
// Documento: /conversations/{auto_generated_id}
{
  userId: "google_auth_uid_123456",       // String - FK a users.uid
  userName: "Pedro García",               // String - Nombre (desnormalizado)
  question: "Quiero un vino tinto",       // String - Pregunta del usuario
  answer: "Te recomiendo un Tempranillo", // String - Respuesta de Sumy
  createdAt: FirebaseTimestamp            // Timestamp - Fecha/hora
}
```

**Características:**
- **Document ID**: Auto-generado por Firestore
- **Propósito**: Historial completo de interacciones
- **Operaciones**: `addDoc` para nuevas conversaciones
- **Consultas**: `where('userId', '==', uid)` + `orderBy('createdAt', 'desc')`

## 🔍 Consultas Implementadas

### Cargar Historial de Usuario
```javascript
const conversationsQuery = query(
  collection(db, 'conversations'),
  where('userId', '==', user.value.uid),
  orderBy('createdAt', 'desc'),
  limit(10)
);
```

### Guardar Nueva Conversación
```javascript
await addDoc(collection(db, 'conversations'), {
  userId: user.value.uid,
  userName: user.value.displayName || 'Usuario',
  question: question || '',
  answer: String(answer),
  createdAt: serverTimestamp()
});
```

### Actualizar Usuario
```javascript
await setDoc(userRef, {
  uid: userData.uid,
  displayName: userData.displayName,
  email: userData.email,
  lastLogin: serverTimestamp(),
}, { merge: true });
```

## 🏗️ Diseño de la Arquitectura

### Ventajas de esta Estructura:

1. **🔐 Seguridad**: Google Auth como identificador único
2. **📈 Escalabilidad**: Firestore maneja automáticamente la escalabilidad
3. **⚡ Performance**: Consultas optimizadas con índices automáticos
4. **🔄 Sincronización**: Datos en tiempo real entre dispositivos
5. **📱 Offline**: Soporte offline nativo de Firestore

### Consideraciones:

- **Desnormalización**: `userName` se guarda en conversaciones para eficiencia
- **Timestamps**: `serverTimestamp()` para consistencia temporal
- **Límites**: Máximo 10 conversaciones cargadas por defecto
- **Validación**: Verificación de datos antes de guardar

## 🔧 Configuración de Seguridad (Firestore Rules)

```javascript
// Reglas de seguridad sugeridas
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Usuarios solo pueden acceder a sus propios datos
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Conversaciones solo accesibles por el propietario
    match /conversations/{conversationId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.userId;
    }
  }
}
```

## 📊 Métricas de Uso

- **Lecturas**: Carga de historial (máximo 10 documentos)
- **Escrituras**: 2 por interacción (usuario + conversación)
- **Almacenamiento**: ~200 bytes por conversación
- **Índices**: Automáticos en `userId` y `createdAt`

## 🚀 Optimizaciones Implementadas

1. **Límite de Consultas**: Solo 10 conversaciones recientes
2. **Merge de Usuarios**: Evita sobrescribir datos existentes
3. **Validación de Datos**: Verificación antes de guardar
4. **Manejo de Errores**: Try-catch en todas las operaciones
5. **Timestamps del Servidor**: Consistencia temporal garantizada

Esta estructura proporciona una base sólida y escalable para el sistema de memoria del Sumiller Virtual. 