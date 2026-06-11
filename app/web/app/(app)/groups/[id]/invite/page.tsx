'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { getGroup } from '@/lib/api/groups'
import { Group } from '@/lib/types'
import { ArrowLeft, Copy, Share2, Check } from 'lucide-react'
import { toast } from 'sonner'

interface GroupInvitePageProps {
  params: Promise<{ id: string }>
}

export default function GroupInvitePage({ params }: GroupInvitePageProps) {
  const { id } = use(params)
  const router = useRouter()
  const [copied, setCopied] = useState<'link' | 'code' | null>(null)
  const [group, setGroup] = useState<Group | undefined>()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadGroup() {
      setIsLoading(true)
      try {
        const nextGroup = await getGroup(id)
        if (!cancelled) setGroup(nextGroup)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadGroup()

    return () => {
      cancelled = true
    }
  }, [id])

  if (!group && !isLoading) {
    return (
      <div className="px-4 py-6 max-w-md mx-auto">
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🤔</div>
          <p className="font-medium">Grupo não encontrado</p>
          <Button variant="outline" className="mt-4" onClick={() => router.back()}>
            Voltar
          </Button>
        </Card>
      </div>
    )
  }

  if (!group) {
    return (
      <div className="px-4 py-6 max-w-md mx-auto">
        <Card className="p-8 text-center">
          <p className="font-medium">Carregando convite...</p>
        </Card>
      </div>
    )
  }

  // inviteLink from the backend may already be absolute (FRONTEND_URL set) or
  // still a relative path from an older deployment – normalise to absolute here.
  const absoluteInviteLink = (() => {
    if (typeof window === 'undefined') return group.inviteLink
    try {
      return new URL(group.inviteLink, window.location.origin).href
    } catch {
      return group.inviteLink
    }
  })()

  const copyToClipboard = (text: string, type: 'link' | 'code') => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    toast.success('Copiado!', {
      description: type === 'link' ? 'Link copiado para a área de transferência' : 'Código copiado para a área de transferência',
    })
    setTimeout(() => setCopied(null), 2000)
  }

  const shareLink = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Entra no bolão ${group.name}!`,
          text: `Vem pro bolão da Copa 2026! Use o código ${group.code} ou clique no link:`,
          url: absoluteInviteLink,
        })
      } catch {
        // User cancelled share
      }
    } else {
      copyToClipboard(absoluteInviteLink, 'link')
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
          <Share2 className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-xl font-bold mb-1">Convide para {group.name}</h1>
        <p className="text-sm text-muted-foreground">
          Compartilhe o código ou link com seus amigos
        </p>
      </div>

      {/* Invite Code */}
      <Card className="p-6 mb-4">
        <p className="text-sm text-muted-foreground mb-2">Código do grupo</p>
        <div className="flex items-center gap-2">
          <Input
            value={group.code}
            readOnly
            className="font-mono text-lg font-bold text-center tracking-widest"
          />
          <Button
            variant="outline"
            size="icon"
            onClick={() => copyToClipboard(group.code, 'code')}
            className="shrink-0"
            aria-label="Copiar código do grupo"
          >
            {copied === 'code' ? (
              <Check className="h-4 w-4 text-success" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        </div>
      </Card>

      {/* Invite Link */}
      <Card className="p-6 mb-6">
        <p className="text-sm text-muted-foreground mb-2">Link de convite</p>
        <div className="flex items-center gap-2">
          <Input
            value={absoluteInviteLink}
            readOnly
            className="text-sm"
          />
          <Button
            variant="outline"
            size="icon"
            onClick={() => copyToClipboard(absoluteInviteLink, 'link')}
            className="shrink-0"
            aria-label="Copiar link de convite"
          >
            {copied === 'link' ? (
              <Check className="h-4 w-4 text-success" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        </div>
      </Card>

      {/* Share Button */}
      <Button 
        className="w-full h-14 text-lg font-semibold rounded-2xl"
        onClick={shareLink}
      >
        <Share2 className="h-5 w-5 mr-2" />
        Compartilhar
      </Button>

      {/* Fun Message */}
      <p className="text-center text-sm text-muted-foreground mt-6">
        Quanto mais gente, melhor a zoeira!
      </p>
    </div>
  )
}
