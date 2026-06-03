'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, UserPlus, Link as LinkIcon } from 'lucide-react'
import { toast } from 'sonner'

export default function JoinGroupPage() {
  const router = useRouter()
  const [code, setCode] = useState('')
  const [isJoining, setIsJoining] = useState(false)

  useEffect(() => {
    const inviteCode = new URLSearchParams(window.location.search).get('code')
    if (!inviteCode) return

    const timeoutId = window.setTimeout(() => {
      setCode(inviteCode.toUpperCase())
    }, 0)

    return () => window.clearTimeout(timeoutId)
  }, [])

  const handleJoin = (event?: React.FormEvent) => {
    event?.preventDefault()
    if (!code.trim()) {
      toast.error('Digite o código do grupo')
      return
    }
    setIsJoining(true)
    // Simulate API call
    setTimeout(() => {
      toast.success('Você entrou no grupo!', {
        description: 'Bem-vindo ao bolão!',
      })
      router.push('/groups')
    }, 500)
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
          <UserPlus className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-xl font-bold mb-1">Entrar em um grupo</h1>
        <p className="text-sm text-muted-foreground">
          Digite o código de convite que você recebeu
        </p>
      </div>

      <form onSubmit={handleJoin}>
        {/* Form */}
        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code">Código do grupo</Label>
              <Input
                id="code"
                placeholder="Ex: FIRMA2026"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                className="h-12 font-mono text-lg tracking-widest text-center uppercase"
                maxLength={20}
              />
            </div>
          </div>
        </Card>

        {/* Info */}
        <div className="mb-6 p-4 rounded-xl bg-muted/50">
          <div className="flex items-start gap-3">
            <LinkIcon className="h-5 w-5 text-muted-foreground mt-0.5 shrink-0" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium text-foreground mb-1">Recebeu um link?</p>
              <p>Se você clicou em um link de convite, o código já foi preenchido automaticamente.</p>
            </div>
          </div>
        </div>

        {/* Join Button */}
        <Button 
          type="submit"
          className="w-full h-14 text-lg font-semibold rounded-2xl"
          disabled={isJoining || !code.trim()}
        >
          {isJoining ? 'Entrando...' : 'Entrar no grupo'}
        </Button>
      </form>
    </div>
  )
}
