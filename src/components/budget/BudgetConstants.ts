export const EXPENSE_CATEGORIES = [
  'Alimentation',
  'Transport',
  'Logement',
  'Loisirs',
  'Santé',
  'Éducation',
  'Shopping',
  'Restaurants',
  'Abonnements',
  'Autre',
] as const

export const INCOME_CATEGORIES = [
  'Salaire',
  'Freelance',
  'Investissements',
  'Remboursements',
  'Autre',
] as const

export const FREQUENCY_LABELS: Record<string, string> = {
  daily: 'Quotidien',
  weekly: 'Hebdomadaire',
  monthly: 'Mensuel',
  yearly: 'Annuel',
}

export const FREQUENCY_SHORT: Record<string, string> = {
  daily: '/jour',
  weekly: '/sem.',
  monthly: '/mois',
  yearly: '/an',
}

export const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  courant: 'Courant',
  epargne: 'Épargne',
  prepaye: 'Prépayé',
}

export const CATEGORY_COLORS: Record<string, string> = {
  Alimentation: '#f59e0b',
  Transport: '#3b82f6',
  Logement: '#8b5cf6',
  Loisirs: '#ec4899',
  Santé: '#10b981',
  Éducation: '#6366f1',
  Shopping: '#f43f5e',
  Restaurants: '#ef4444',
  Abonnements: '#78716c',
  Salaire: '#22c55e',
  Freelance: '#14b8a6',
  Investissements: '#a855f7',
  Remboursements: '#06b6d4',
  Autre: '#a8a29e',
}
