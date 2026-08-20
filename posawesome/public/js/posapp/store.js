// Cross-page hand-off slot.
//
// Home.vue renders pages through `<component :is="page">` with no <keep-alive>,
// so switching pages destroys Pos.vue and Invoice.vue. An order picked on the
// Ecommerce Orders page therefore cannot be handed over on the event bus — the
// cart that would listen for it does not exist yet at the moment of the click.
// Instead the page parks the order here and Invoice.vue claims it once it is
// mounted and has its POS profile, which is deterministic rather than a race.

export const posStore = {
  pending_ecommerce_order: null,
};
