<template>
  <div class="wine-menu-modal" v-if="isVisible" @click.self="$emit('close')">
    <div class="wine-menu-content">
      <!-- Botón de cerrar -->
      <button 
        @click="$emit('close')" 
        class="close-button"
        aria-label="Cerrar carta de vinos"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>

      <!-- Contenido de la carta -->
      <div class="wine-menu-scroll">
        <div class="wine-menu-container">
          
          <header class="text-center mb-12">
            <p class="font-serif text-lg">Mi proyecto TFM</p>
            <h1 class="font-serif text-6xl md:text-7xl mt-2 wine-title">Carta de Vinos</h1>
          </header>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-10">

            <!-- Columna Izquierda -->
            <div>
              <!-- Vinos Blancos -->
              <section class="mb-10">
                <h2 class="font-serif text-4xl mb-6 wine-title">Vinos Blancos</h2>
                <div class="space-y-5">
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Belondrade & Lurtón</h3>
                      <span class="wine-price">45.00€</span>
                    </div>
                    <p class="wine-description">Verdejo | D.O. Rueda. Un icono, fermentado en barrica, complejo y untuoso.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Vindel</h3>
                      <span class="wine-price">38.00€</span>
                    </div>
                    <p class="wine-description">Albariño | D.O. Rías Baixas. Glicérico y sedoso, con notas de fruta de hueso y membrillo.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Javier Sanz V Malcorta</h3>
                      <span class="wine-price">26.00€</span>
                    </div>
                    <p class="wine-description">Verdejo Malcorta | D.O. Rueda. Cítricos, flores blancas y marcada acidez.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">La Capilla</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Verdejo, Sauvignon Blanc | D.O. Rueda. Nariz rica con fruta blanca, minerales y tostados finos.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Viñas del Vero Gewürztraminer</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Gewürztraminer | D.O. Somontano. Aroma floral embriagador con fruta exótica.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Enate 234 Chardonnay</h3>
                      <span class="wine-price">21.00€</span>
                    </div>
                    <p class="wine-description">Chardonnay | D.O. Somontano. Vendimia manual, fresco y versátil.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Naia</h3>
                      <span class="wine-price">21.00€</span>
                    </div>
                    <p class="wine-description">Verdejo | D.O. Rueda. Gran relación calidad-precio. Tipicidad y coherencia.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Martín Códax</h3>
                      <span class="wine-price">20.00€</span>
                    </div>
                    <p class="wine-description">Albariño | D.O. Rías Baixas. Expresivo y aromático. Ideal con frutos del mar.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Don Pedro de Soutomaior</h3>
                      <span class="wine-price">20.00€</span>
                    </div>
                    <p class="wine-description">Albariño | D.O. Rías Baixas. Aromas de fruta madura, piña, maracuyá y florales.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Vionta Godello</h3>
                      <span class="wine-price">20.00€</span>
                    </div>
                    <p class="wine-description">Godello | D.O. Monterrei. Afrutado a manzana verde y pera. Equilibrio perfecto.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">El Loco de Finca La Colina</h3>
                      <span class="wine-price">19.00€</span>
                    </div>
                    <p class="wine-description">Verdejo, Sauvignon Blanc | D.O. Rueda. Aromas a mango, melocotón y piña con toques herbáceos.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Terras do Cigarrón Godello</h3>
                      <span class="wine-price">18.00€</span>
                    </div>
                    <p class="wine-description">Godello | D.O. Monterrei. Notas florales blancas, tropicales y especiados. Frescura y elegancia.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Añares Torrenova</h3>
                      <span class="wine-price">17.00€</span>
                    </div>
                    <p class="wine-description">Verdejo | D.O. Rueda. Nariz franca con frutas blancas, notas minerales y miel.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Alba Martín</h3>
                      <span class="wine-price">17.00€</span>
                    </div>
                    <p class="wine-description">Albariño | D.O. Rías Baixas. Reflejo del Val do Salnés. Fresco, frutal y final ligeramente salino.</p>
                  </div>
                </div>
              </section>

              <!-- Vinos Rosados -->
              <section>
                <h2 class="font-serif text-4xl mb-6 wine-title">Vinos Rosados</h2>
                <div class="space-y-5">
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Lou Rosé</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Cinsault, Garnacha | Côtes de Provence. Frutosidad intensa de grosella y fresa.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Chivite Las Fincas Rosado</h3>
                      <span class="wine-price">23.00€</span>
                    </div>
                    <p class="wine-description">Garnacha, Tempranillo | V.T. Tierra Tres Riberas. Suave, equilibrado y muy frutal.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Enate Cabernet Sauvignon</h3>
                      <span class="wine-price">21.00€</span>
                    </div>
                    <p class="wine-description">Cabernet Sauvignon | D.O. Somontano. Con alma de blanco y cuerpo de tinto.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Garnacha Rosado Sotomanrique</h3>
                      <span class="wine-price">17.00€</span>
                    </div>
                    <p class="wine-description">Garnacha | D.O.P. Cebreros. Elegante, complejo y fresco con notas de frutos rojos y jazmín.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Amatista Moscato Rosado</h3>
                      <span class="wine-price">17.00€</span>
                    </div>
                    <p class="wine-description">Moscatel, Garnacha | D.O. Valencia. Dulce, ligero y refrescante con solo 5% de alcohol.</p>
                  </div>
                </div>
              </section>
            </div>

            <!-- Columna Derecha -->
            <div>
              <!-- Vinos Espumosos -->
              <section class="mb-10">
                <h2 class="font-serif text-4xl mb-6 wine-title">Vinos Espumosos</h2>
                <div class="space-y-5">
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Louis Roederer Cristal</h3>
                      <span class="wine-price">225.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. Una leyenda de textura sedosa y potencial mineral.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Dom Pérignon</h3>
                      <span class="wine-price">199.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. El estandarte de la calidad, solo en añadas extraordinarias.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Taittinger Prestige Rosé</h3>
                      <span class="wine-price">75.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. Suculento, afrutado y muy equilibrado.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Veuve Clicquot Yellow Label</h3>
                      <span class="wine-price">60.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. Un icono internacional, el legado de la Viuda Clicquot.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Taittinger Brut Réserve</h3>
                      <span class="wine-price">55.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. Delicado con sabores a fruta fresca y miel.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Moët & Chandon Brut Impérial</h3>
                      <span class="wine-price">50.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. El champagne más emblemático de la Maison.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Henri Abele Brut</h3>
                      <span class="wine-price">43.00€</span>
                    </div>
                    <p class="wine-description">Champagne | A.O.C. Champagne. Dorado con notas de pan tostado, miel y canela.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Segura Viudas Torre Galimany</h3>
                      <span class="wine-price">25.00€</span>
                    </div>
                    <p class="wine-description">Cava | D.O. Cava Cataluña. Fruta sobre madera, tropical y flores blancas con fondo especiado.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Botani Espumoso</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Espumoso | Sierras de Málaga. Aromático con recuerdos a flores blancas, panadería y moscatel.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">André Delorme Rosé Brut</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Crémant | Crémant Bourgogne. Rosa salmón brillante. Notas de fresas y frutas rojas.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">André Delorme Blanc de Blanc Crémant</h3>
                      <span class="wine-price">22.00€</span>
                    </div>
                    <p class="wine-description">Crémant | Crémant Bourgogne. Nariz de bollería y melocotón, burbuja finísima.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Freixenet Trepat Rosado</h3>
                      <span class="wine-price">21.00€</span>
                    </div>
                    <p class="wine-description">Cava | D.O. Cava Cataluña. Burbuja fina. Aromas de frutas rojas silvestres y cítricos.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Beso de Rechenna Brut Nature</h3>
                      <span class="wine-price">20.00€</span>
                    </div>
                    <p class="wine-description">Cava | D.O. Cava Utiel Requena. Textura cremosa y aromas de fruta blanca madura.</p>
                  </div>
                </div>
              </section>
              
              <!-- Vinos Generosos -->
              <section>
                <h2 class="font-serif text-4xl mb-6 wine-title">Vinos Generosos</h2>
                <div class="space-y-5">
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Tío Pepe 3 Palmas</h3>
                      <span class="wine-price">44.00€</span>
                    </div>
                    <p class="wine-description">Fino | D.O. Jerez. Joya de producción limitada. Final salino y cremoso.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Gran Barquero Palo Cortado</h3>
                      <span class="wine-price">37.00€</span>
                    </div>
                    <p class="wine-description">Palo Cortado | D.O. Montilla Moriles. Nariz fina y cuerpo de oloroso.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Medium Carvajal</h3>
                      <span class="wine-price">36.00€</span>
                    </div>
                    <p class="wine-description">Medium | D.O. Jerez. Castaño con reflejos verdosos. Textura sedosa y golosa.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Gran Barquero Amontillado</h3>
                      <span class="wine-price">26.00€</span>
                    </div>
                    <p class="wine-description">Amontillado | D.O. Montilla Moriles. Muy estructurado, con 25 a 30 años de crianza.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Tío Pepe en Rama</h3>
                      <span class="wine-price">24.00€</span>
                    </div>
                    <p class="wine-description">Fino | D.O. Jerez. En estado puro, sin filtrar. Color oro pálido con flor en suspensión.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Alfonso Oloroso Seco</h3>
                      <span class="wine-price">23.00€</span>
                    </div>
                    <p class="wine-description">Oloroso | D.O. Jerez. Gran carácter, ideal para carnes rojas y de caza.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Viña AB Amontillado</h3>
                      <span class="wine-price">22.00€</span>
                    </div>
                    <p class="wine-description">Amontillado | D.O. Jerez. Color ámbar característico tras 8 años en botas de roble.</p>
                  </div>
                  <div class="wine-entry">
                    <div class="flex justify-between items-baseline">
                      <h3 class="text-lg font-semibold">Tío Pepe</h3>
                      <span class="wine-price">18.00€</span>
                    </div>
                    <p class="wine-description">Fino | D.O. Jerez. El clásico, fantásticamente refrescante.</p>
                  </div>
                </div>
              </section>
            </div>
          </div>

          <footer class="text-center mt-16 pt-8 border-t border-t-[rgba(224,208,200,0.1)]">
            <div class="flex flex-col md:flex-row items-center justify-center gap-6">
              <img src="https://i.ibb.co/YFFRkntD/sumi.png" alt="Logo de Sumy, el sumiller IA" class="h-20 w-20 rounded-full object-cover border-2 border-[rgba(224,208,200,0.5)]">
              <div class="flex items-center gap-4">
                <div>
                  <p class="font-serif text-base">Hable con Sumy, tu sumiller personal</p>
                  <p class="text-xs text-gray-400">Escanea el código para recomendaciones</p>
                </div>
                <div class="bg-white p-2 rounded-md inline-block shadow-lg">
                  <img src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=https://maitre-ia.web.app/" alt="Código QR para la carta digital">
                </div>
              </div>
            </div>
          </footer>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WineMenu',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  mounted() {
    // Cerrar con ESC
    if (this.isVisible) {
      document.addEventListener('keydown', this.handleEscKey);
    }
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleEscKey);
  },
  watch: {
    isVisible(newVal) {
      if (newVal) {
        document.addEventListener('keydown', this.handleEscKey);
        // Prevenir scroll del body
        document.body.style.overflow = 'hidden';
      } else {
        document.removeEventListener('keydown', this.handleEscKey);
        // Restaurar scroll del body
        document.body.style.overflow = '';
      }
    }
  },
  methods: {
    handleEscKey(event) {
      if (event.key === 'Escape') {
        this.$emit('close');
      }
    }
  }
}
</script>

<style scoped>
/* Importar fuentes */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Poppins:wght@300;400&display=swap');

/* Modal backdrop */
.wine-menu-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

/* Contenido del modal */
.wine-menu-content {
  position: relative;
  background-color: #4a2c3e;
  color: #fdeae0;
  width: 95%;
  height: 95%;
  max-width: 1200px;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  background-image:
    radial-gradient(circle at 100% 100%, #603950 0%, transparent 40%),
    radial-gradient(circle at 0% 0%, #603950 0%, transparent 30%);
}

/* Área de scroll */
.wine-menu-scroll {
  height: 100%;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #fdeae0 #4a2c3e;
}

.wine-menu-scroll::-webkit-scrollbar {
  width: 8px;
}

.wine-menu-scroll::-webkit-scrollbar-track {
  background: #4a2c3e;
}

.wine-menu-scroll::-webkit-scrollbar-thumb {
  background: #fdeae0;
  border-radius: 4px;
}

.wine-menu-scroll::-webkit-scrollbar-thumb:hover {
  background: #e0d0c8;
}

/* Container interno */
.wine-menu-container {
  padding: 2rem;
  font-family: 'Poppins', sans-serif;
}

/* Botón de cerrar */
.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  width: 40px;
  height: 40px;
  background-color: rgba(253, 234, 224, 0.1);
  border: 2px solid rgba(253, 234, 224, 0.3);
  border-radius: 50%;
  color: #fdeae0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

.close-button:hover {
  background-color: rgba(253, 234, 224, 0.2);
  border-color: rgba(253, 234, 224, 0.6);
  transform: scale(1.1);
}

.close-button svg {
  width: 20px;
  height: 20px;
}

/* Estilos de la carta */
.font-serif {
  font-family: 'Playfair Display', serif;
}

.wine-title {
  color: #fdeae0;
}

.wine-price {
  color: #fdeae0;
  font-weight: 400;
}

.wine-description {
  color: #e0d0c8;
  font-size: 0.9em;
  font-weight: 300;
}

.wine-entry {
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(224, 208, 200, 0.1);
}

.wine-entry:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* Grid responsivo */
.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.gap-x-16 {
  column-gap: 4rem;
}

.gap-y-10 {
  row-gap: 2.5rem;
}

/* Utilidades de espaciado */
.space-y-5 > * + * {
  margin-top: 1.25rem;
}

.mb-10 {
  margin-bottom: 2.5rem;
}

.mb-12 {
  margin-bottom: 3rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-16 {
  margin-top: 4rem;
}

.pt-8 {
  padding-top: 2rem;
}

/* Flexbox */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.flex-row {
  flex-direction: row;
}

.items-center {
  align-items: center;
}

.items-baseline {
  align-items: baseline;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-4 {
  gap: 1rem;
}

.gap-6 {
  gap: 1.5rem;
}

/* Texto */
.text-center {
  text-align: center;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.text-4xl {
  font-size: 2.25rem;
  line-height: 2.5rem;
}

.text-6xl {
  font-size: 3.75rem;
  line-height: 1;
}

.text-base {
  font-size: 1rem;
  line-height: 1.5rem;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.font-semibold {
  font-weight: 600;
}

/* Responsive text */
@media (min-width: 768px) {
  .md\:text-7xl {
    font-size: 4.5rem;
    line-height: 1;
  }
  
  .md\:flex-row {
    flex-direction: row;
  }
}

/* Bordes */
.border-t {
  border-top-width: 1px;
}

.border-2 {
  border-width: 2px;
}

.rounded-full {
  border-radius: 9999px;
}

.rounded-md {
  border-radius: 0.375rem;
}

/* Objetos */
.object-cover {
  object-fit: cover;
}

/* Tamaños */
.h-20 {
  height: 5rem;
}

.w-20 {
  width: 5rem;
}

/* Sombras */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Background */
.bg-white {
  background-color: white;
}

.inline-block {
  display: inline-block;
}

/* Color de texto específico */
.text-gray-400 {
  color: #9ca3af;
}

/* Responsive */
@media (max-width: 768px) {
  .wine-menu-container {
    padding: 1rem;
  }
  
  .text-6xl {
    font-size: 2.5rem;
  }
  
  .text-4xl {
    font-size: 1.875rem;
  }
  
  .gap-x-16 {
    column-gap: 1rem;
  }
  
  .close-button {
    top: 0.5rem;
    right: 0.5rem;
  }
}
</style> 