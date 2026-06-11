'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Users, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { ApiError } from '@/lib/api/client'
import { createGroup } from '@/lib/api/groups'
import { useApp } from '@/lib/context'

export default function CreateGroupPage() {
  const router = useRouter()
  const { refreshGroups, setCurrentGroup } = useApp()
  const [name, setName] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const handleCreate = async (event?: React.FormEvent) => {
    event?.preventDefault()
    if (!name.trim()) {
      toast.error('Digite um nome para o grupo')
      return
    }
    setIsCreating(true)
    try {
      const group = await createGroup(name.trim())
      if (group) setCurrentGroup(group)
      await refreshGroups()
      toast.success('Grupo criado!', {
        description: `O grupo "${name}" foi criado com sucesso`,
      })
      router.push('/groups')
    } catch (error) {
      toast.error('Não foi possível criar o grupo', {
        description: error instanceof ApiError ? error.message : 'Tente novamente em instantes',
      })
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="px-4 py-6 max-w-md mx-auto">
      {/* Back Button */}
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => router.back()}
        className="mb-4 -ml-2"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Voltar
      </Button>

      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
          <Users className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-xl font-bold mb-1">Criar novo grupo</h1>
        <p className="text-sm text-muted-foreground">
          Crie um bolão e convide seus amigos
        </p>
      </div>

      <form onSubmit={handleCreate}>
        {/* Form */}
        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome do grupo</Label>
              <Input
                id="name"
                placeholder="Ex: Bolão da Firma"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="h-12"
              />
            </div>
          </div>
        </Card>

        {/* Suggestions */}
        <div className="mb-6">
          <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            Sugestões de nome
          </p>
          <div className="flex flex-wrap gap-2">
            {['Bolão da Firma', 'Família Boleira', 'Os Palpiteiros', 'Bolão do Churrasco'].map((suggestion) => (
              <Button
                key={suggestion}
                type="button"
                variant="outline"
                size="sm"
                className="text-xs rounded-full"
                onClick={() => setName(suggestion)}
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>

        {/* Create Button */}
        <Button 
          type="submit"
          className="w-full h-14 text-lg font-semibold rounded-2xl"
          disabled={isCreating || !name.trim()}
        >
          {isCreating ? 'Criando...' : 'Criar grupo'}
        </Button>
      </form>
    </div>
  )
}
