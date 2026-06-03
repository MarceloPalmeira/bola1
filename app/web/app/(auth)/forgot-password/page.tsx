'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Trophy, ArrowLeft, Mail } from 'lucide-react'
import { toast } from 'sonner'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) {
      toast.error('Digite seu e-mail')
      return
    }
    setIsLoading(true)
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false)
      setSubmitted(true)
    }, 500)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
            <Trophy className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-primary">bola1</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Recuperar senha
          </p>
        </div>

        {/* Card */}
        <Card className="p-6">
          {submitted ? (
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-4">
                <Mail className="h-8 w-8 text-success" />
              </div>
              <h2 className="text-lg font-semibold mb-2">Verifique seu e-mail</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Enviamos um link de recuperação para <strong>{email}</strong>
              </p>
              <Link href="/login">
                <Button variant="outline" className="w-full">
                  Voltar para o login
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <p className="text-sm text-muted-foreground text-center mb-6">
                Digite seu e-mail e enviaremos um link para redefinir sua senha.
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">E-mail</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-12"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full h-12 text-lg font-semibold rounded-xl"
                  disabled={isLoading}
                >
                  {isLoading ? 'Enviando...' : 'Enviar link'}
                </Button>
              </form>
              <Link href="/login" className="block mt-6">
                <Button variant="ghost" className="w-full">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Voltar para o login
                </Button>
              </Link>
            </>
          )}
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6">
          Um bolão de amigos. Sem apostas reais.
        </p>
      </div>
    </div>
  )
}
