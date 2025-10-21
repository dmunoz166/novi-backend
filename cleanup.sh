#!/bin/bash
set -e

echo "🧹 Limpiando recursos para testing..."

# Limpiar agentes existentes
EXISTING_AGENTS=$(aws bedrock-agent list-agents --region us-west-2 --query 'agentSummaries[?agentName==`novi-pqr-agent`].agentId' --output text)

if [ ! -z "$EXISTING_AGENTS" ]; then
    for AGENT_ID in $EXISTING_AGENTS; do
        echo "  Eliminando aliases del agente $AGENT_ID..."
        ALIASES=$(aws bedrock-agent list-agent-aliases --agent-id $AGENT_ID --region us-west-2 --query 'agentAliasSummaries[?agentAliasId!=`TSTALIASID`].agentAliasId' --output text 2>/dev/null || echo "")
        
        for ALIAS_ID in $ALIASES; do
            aws bedrock-agent delete-agent-alias --agent-id $AGENT_ID --agent-alias-id $ALIAS_ID --region us-west-2 > /dev/null 2>&1 || true
        done
        
        sleep 10
        
        echo "  Eliminando agente $AGENT_ID..."
        aws bedrock-agent delete-agent --agent-id $AGENT_ID --skip-resource-in-use-check --region us-west-2 > /dev/null 2>&1 || true
    done
fi

echo "✅ Limpieza completada"
